"""WhisperRuntimeAdapter — the Snapdragon Whisper ``SpeechToTextEngine``.

Implements the existing ``SpeechToTextEngine`` interface (unchanged) using
the ONNX Runtime + QNN Execution Provider runtime path STEP 9 investigated
and verified. This class orchestrates, in order: model-path existence
checks, the device compatibility guard, tokenizer/feature-extractor
construction, encoder/decoder session construction, the autoregressive
decode loop, and ``TranscriptSegment`` construction — importing no
optional runtime dependency at module load time (see
runtime/README.md "Optional dependency strategy").

CRITICAL: constructing and calling this adapter has not been validated
against real Windows-on-Snapdragon hardware, a real ``onnxruntime-qnn``
installation, or a real ``transformers`` installation, in this step. This
class implements the adapter *architecture* and testable boundary only —
see runtime/README.md "What remains hardware-dependent".
"""

from __future__ import annotations

import os
from typing import Optional, Sequence

from perception_firewall.domain.transcript import TranscriptSegment, TranscriptSource
from perception_firewall.interfaces.audio import AudioChunk
from perception_firewall.interfaces.errors import SpeechRecognitionError
from perception_firewall.interfaces.speech_to_text import SpeechToTextEngine
from perception_firewall.runtime.config import WhisperRuntimeConfig
from perception_firewall.runtime.decoder_loop import run_decoder_loop, run_encoder
from perception_firewall.runtime.feature_extraction import (
    TransformersWhisperFeatureExtractor,
    WhisperFeatureExtractor,
)
from perception_firewall.runtime.platform_guard import (
    PlatformInfo,
    check_snapdragon_windows_host,
)
from perception_firewall.runtime.sessions import WhisperDecoderSession, WhisperEncoderSession
from perception_firewall.runtime.tokenizer import (
    TransformersWhisperTokenizer,
    WhisperTokenizer,
)


class WhisperRuntimeAdapter(SpeechToTextEngine):
    """Whisper-on-Snapdragon ``SpeechToTextEngine`` implementation.

    Every dependency this class needs — model paths, tokenizer source,
    decode parameters — comes from the injected ``WhisperRuntimeConfig``;
    nothing is hard-coded. ``platform_info``, ``tokenizer``,
    ``feature_extractor``, and the encoder/decoder sessions are all
    injectable so this class can be constructed and its non-runtime logic
    tested without the optional ``transformers``/``onnxruntime``
    dependencies or real Snapdragon hardware — but production callers
    should leave them unset and get the real implementations, which fail
    clearly (``SpeechRecognitionError``) if their optional dependency is
    unavailable, rather than silently falling back to anything fake.
    """

    def __init__(
        self,
        config: WhisperRuntimeConfig,
        platform_info: Optional[PlatformInfo] = None,
        tokenizer: Optional[WhisperTokenizer] = None,
        feature_extractor: Optional[WhisperFeatureExtractor] = None,
        encoder_session: Optional[WhisperEncoderSession] = None,
        decoder_session: Optional[WhisperDecoderSession] = None,
    ) -> None:
        if not isinstance(config, WhisperRuntimeConfig):
            raise SpeechRecognitionError(
                "WhisperRuntimeAdapter requires a WhisperRuntimeConfig, got "
                f"{type(config).__name__!r}"
            )

        if not os.path.isfile(config.model_paths.encoder_path):
            raise SpeechRecognitionError(
                "Whisper encoder model file not found at "
                f"{config.model_paths.encoder_path!r}."
            )
        if not os.path.isfile(config.model_paths.decoder_path):
            raise SpeechRecognitionError(
                "Whisper decoder model file not found at "
                f"{config.model_paths.decoder_path!r}."
            )

        host_info = platform_info or PlatformInfo.from_current_host()
        compatibility = check_snapdragon_windows_host(host_info)
        if not compatibility.is_compatible:
            raise SpeechRecognitionError(
                "This host does not appear compatible with the Whisper "
                f"Snapdragon runtime path: {compatibility.reason}"
            )

        self._config = config
        self._tokenizer: WhisperTokenizer = tokenizer or TransformersWhisperTokenizer(
            config.tokenizer_config
        )
        self._feature_extractor: WhisperFeatureExtractor = (
            feature_extractor
            or TransformersWhisperFeatureExtractor(config.tokenizer_config)
        )

        if encoder_session is not None and decoder_session is not None:
            self._encoder_session = encoder_session
            self._decoder_session = decoder_session
        elif encoder_session is not None or decoder_session is not None:
            raise SpeechRecognitionError(
                "WhisperRuntimeAdapter requires both encoder_session and "
                "decoder_session to be injected together, or neither."
            )
        else:
            # Lazy import: onnx_sessions.py itself guards its own optional
            # onnxruntime import, so importing this module is always safe.
            from perception_firewall.runtime.onnx_sessions import (
                WhisperOnnxDecoderSession,
                WhisperOnnxEncoderSession,
            )

            self._encoder_session = WhisperOnnxEncoderSession(
                config.model_paths.encoder_path
            )
            self._decoder_session = WhisperOnnxDecoderSession(
                config.model_paths.decoder_path, config.decode_config.max_decode_length
            )

    def transcribe(self, audio: AudioChunk) -> Sequence[TranscriptSegment]:
        if audio is None or not isinstance(audio, AudioChunk):
            raise SpeechRecognitionError(
                "WhisperRuntimeAdapter.transcribe() requires an AudioChunk, "
                f"got {type(audio).__name__!r}"
            )

        try:
            input_features = self._feature_extractor.extract(
                audio.data, audio.sample_rate_hz
            )
            encoder_output = run_encoder(self._encoder_session, input_features)
            result = run_decoder_loop(
                self._decoder_session,
                encoder_output,
                start_of_transcript_token_id=self._tokenizer.start_of_transcript_token_id,
                eot_token_id=self._tokenizer.eot_token_id,
                max_decode_length=self._config.decode_config.max_decode_length,
            )
            text = self._tokenizer.decode(result.token_ids)
        except SpeechRecognitionError:
            raise
        except Exception as exc:
            raise SpeechRecognitionError(
                f"Whisper transcription failed: {exc}"
            ) from exc

        if not text.strip():
            return ()

        # AudioChunk (see interfaces/audio.py) carries raw bytes plus
        # sample_rate_hz/channels, but no duration field, and no declared
        # sample bit depth/format — so an exact audio-relative duration
        # cannot be computed from the input contract alone without
        # assuming a sample format nothing here confirms. Fabricating one
        # was explicitly disallowed, so both timestamps are anchored at
        # 0.0 (TranscriptSegment permits a zero-length segment — see
        # domain/transcript.py). See runtime/README.md "Known limitation:
        # timing precision" for the full discussion and what a future
        # AudioChunk extension would need to add to resolve this.
        segment = TranscriptSegment(
            segment_id=f"whisper-{audio.sequence_number}",
            text=text,
            start_time=0.0,
            end_time=0.0,
            source=TranscriptSource.LIVE_AUDIO,
        )
        return (segment,)

"""MockSpeechToTextEngine — a TEST DOUBLE, not a speech recognizer.

This class performs no speech recognition whatsoever. It maps a known
fixture identifier (carried on ``AudioChunk.fixture_id``) to a fixed,
pre-written sequence of ``TranscriptSegment`` objects. It exists purely so
the rest of the application pipeline can be built and tested on the
developer's Mac, which cannot run the real Whisper-on-Qualcomm-NPU engine.

Do not use this class's output as evidence of real transcription accuracy,
and do not present it as if it ran on Snapdragon hardware.
"""

from __future__ import annotations

from typing import Mapping, Optional, Sequence

from perception_firewall.domain.transcript import TranscriptSegment, TranscriptSource
from perception_firewall.interfaces.audio import AudioChunk
from perception_firewall.interfaces.errors import SpeechRecognitionError
from perception_firewall.interfaces.speech_to_text import SpeechToTextEngine

#: Deterministic fixture scenarios. Keys are fixture identifiers a
#: development/test AudioSource can set on ``AudioChunk.fixture_id``.
DEFAULT_FIXTURES: Mapping[str, Sequence[TranscriptSegment]] = {
    "demo_silence": (),
    "demo_normal": (
        TranscriptSegment(
            segment_id="demo_normal-1",
            text="Hello, how are you? I wanted to confirm tomorrow's meeting.",
            start_time=0.0,
            end_time=3.2,
            source=TranscriptSource.RECORDED_AUDIO,
        ),
    ),
    "demo_bank_otp": (
        TranscriptSegment(
            segment_id="demo_bank_otp-1",
            text="Your bank account will be blocked today.",
            start_time=0.0,
            end_time=2.1,
            source=TranscriptSource.RECORDED_AUDIO,
        ),
        TranscriptSegment(
            segment_id="demo_bank_otp-2",
            text="Give me the OTP immediately.",
            start_time=2.1,
            end_time=3.8,
            source=TranscriptSource.RECORDED_AUDIO,
        ),
    ),
    "demo_remote_access": (
        TranscriptSegment(
            segment_id="demo_remote_access-1",
            text=(
                "Install AnyDesk and give me remote access so I can "
                "verify your account."
            ),
            start_time=0.0,
            end_time=4.5,
            source=TranscriptSource.RECORDED_AUDIO,
        ),
    ),
    "demo_authority_payment": (
        TranscriptSegment(
            segment_id="demo_authority_payment-1",
            text="I am calling from the authorities.",
            start_time=0.0,
            end_time=1.9,
            source=TranscriptSource.RECORDED_AUDIO,
        ),
        TranscriptSegment(
            segment_id="demo_authority_payment-2",
            text=(
                "You need to transfer the payment immediately or legal "
                "action will follow."
            ),
            start_time=1.9,
            end_time=5.4,
            source=TranscriptSource.RECORDED_AUDIO,
        ),
    ),
}


class MockSpeechToTextEngine(SpeechToTextEngine):
    """TEST DOUBLE. Returns fixed transcript segments for known fixture IDs.

    Not a speech recognizer. Never attempts to interpret audio bytes.
    """

    def __init__(
        self, fixtures: Optional[Mapping[str, Sequence[TranscriptSegment]]] = None
    ) -> None:
        self._fixtures: Mapping[str, Sequence[TranscriptSegment]] = (
            dict(fixtures) if fixtures is not None else dict(DEFAULT_FIXTURES)
        )

    def transcribe(self, audio: AudioChunk) -> Sequence[TranscriptSegment]:
        if audio is None:
            raise SpeechRecognitionError(
                "MockSpeechToTextEngine.transcribe() received no audio"
            )

        fixture_id = audio.fixture_id
        if fixture_id is None:
            raise SpeechRecognitionError(
                "MockSpeechToTextEngine requires AudioChunk.fixture_id to "
                "be set to a known fixture identifier; it does not perform "
                "real speech recognition"
            )

        if fixture_id not in self._fixtures:
            raise SpeechRecognitionError(
                f"MockSpeechToTextEngine has no fixture registered for "
                f"fixture_id={fixture_id!r}"
            )

        return self._fixtures[fixture_id]

"""Concrete Whisper encoder/decoder sessions: ONNX Runtime + the
Qualcomm QNN Execution Provider.

This is a real implementation of the runtime path STEP 9 investigated and
verified by direct inspection of the installed Qualcomm SDK
(``qai_hub_models.utils.onnx.torch_wrapper.OnnxModelTorchWrapper.OnNPU``)
— it is NOT a mock and must never be used as one. ``onnxruntime`` (and the
``numpy`` it transitively requires) are imported lazily, inside
``__init__``, never at module import time, so importing this *module* is
always safe; only *constructing* one of these classes requires the
optional runtime dependency to actually be installed.

IMPORTANT: this code has not been exercised against real
Windows-on-Snapdragon hardware or a real ``onnxruntime`` +
``onnxruntime-qnn`` installation in this step — that validation is a
later, hardware-dependent step. See runtime/README.md "What remains
hardware-dependent".

Nothing about the decoder's architecture (layer count, head count, head
dimension) is hard-coded here — the self-attention KV cache tensor names,
count, and shapes are introspected from the loaded ONNX graph's own
declared inputs/outputs at construction time, the same way
``qai_hub_models.utils.onnx.helpers.extract_io_types_from_onnx_model``
does it.
"""

from __future__ import annotations

from typing import Optional, Tuple

from perception_firewall.interfaces.errors import SpeechRecognitionError
from perception_firewall.runtime.sessions import (
    DecoderStepOutput,
    EncoderOutput,
    WhisperDecoderSession,
    WhisperEncoderSession,
)

#: Negative fill value for masked (not-yet-generated) attention
#: positions. STEP 9's reference harness
#: (qai_hub_models.models.templates.hf_whisper.model / app.py) uses a
#: config-supplied ``mask_neg`` constant for exactly this purpose; -100.0
#: is used here as a conservative, sufficiently-negative fill for a
#: float16 softmax mask (float16's usable negative range is roughly
#: -65504, so -100 reliably drives masked positions' softmax weight to
#: ~0 without risking float16 overflow the way a much larger magnitude
#: could).
_ATTENTION_MASK_NEG_FILL = -100.0

_QNN_EXECUTION_PROVIDER = "QNNExecutionProvider"


def _import_onnx_runtime_dependencies():
    try:
        import numpy as np
        import onnxruntime as ort
    except ImportError as exc:
        raise SpeechRecognitionError(
            "The Whisper Snapdragon runtime requires the optional "
            "'onnxruntime' package (built with QNN Execution Provider "
            "support) and its 'numpy' dependency, neither of which is "
            "installed in this environment. This is intentionally not a "
            "core application dependency — see runtime/README.md."
        ) from exc
    return np, ort


class WhisperOnnxEncoderSession(WhisperEncoderSession):
    """Loads ``encoder.onnx`` via ``onnxruntime.InferenceSession`` with
    the QNN Execution Provider and runs it once per audio chunk."""

    def __init__(self, model_path: str) -> None:
        _np, ort = _import_onnx_runtime_dependencies()
        try:
            self._session = ort.InferenceSession(
                model_path, providers=[_QNN_EXECUTION_PROVIDER]
            )
        except Exception as exc:
            raise SpeechRecognitionError(
                f"Failed to create the Whisper encoder ONNX Runtime session "
                f"from {model_path!r}: {exc}"
            ) from exc

        self._output_names = [o.name for o in self._session.get_outputs()]
        self._input_name = self._session.get_inputs()[0].name

    def run(self, input_features: object) -> EncoderOutput:
        try:
            outputs = self._session.run(
                self._output_names, {self._input_name: input_features}
            )
        except Exception as exc:
            raise SpeechRecognitionError(
                f"Whisper encoder inference failed: {exc}"
            ) from exc
        return EncoderOutput(cross_attention_kv=tuple(outputs))


class WhisperOnnxDecoderSession(WhisperDecoderSession):
    """Loads ``decoder.onnx`` via ``onnxruntime.InferenceSession`` with
    the QNN Execution Provider and runs one autoregressive step at a
    time. Owns all tensor construction (zero KV-cache init, sliding
    attention-mask/position-id construction) per the
    ``WhisperDecoderSession`` contract.
    """

    def __init__(self, model_path: str, max_decode_length: int) -> None:
        np, ort = _import_onnx_runtime_dependencies()
        self._np = np
        self._max_decode_length = max_decode_length

        try:
            self._session = ort.InferenceSession(
                model_path, providers=[_QNN_EXECUTION_PROVIDER]
            )
        except Exception as exc:
            raise SpeechRecognitionError(
                f"Failed to create the Whisper decoder ONNX Runtime session "
                f"from {model_path!r}: {exc}"
            ) from exc

        input_specs = {i.name: i for i in self._session.get_inputs()}
        output_specs = {o.name: o for o in self._session.get_outputs()}

        self._self_kv_in_names = sorted(
            name
            for name in input_specs
            if name.startswith("k_cache_self_") or name.startswith("v_cache_self_")
        )
        self._self_kv_out_names = sorted(
            name
            for name in output_specs
            if name.startswith("k_cache_self_") or name.startswith("v_cache_self_")
        )
        self._cross_kv_names = sorted(
            name
            for name in input_specs
            if name.startswith("k_cache_cross_") or name.startswith("v_cache_cross_")
        )

        if not self._self_kv_in_names or len(self._self_kv_in_names) != len(
            self._self_kv_out_names
        ):
            raise SpeechRecognitionError(
                f"Whisper decoder ONNX graph at {model_path!r} does not "
                "expose the expected self-attention KV cache input/output "
                "tensors (k_cache_self_*/v_cache_self_*); cannot proceed."
            )
        if "input_ids" not in input_specs or "position_ids" not in input_specs:
            raise SpeechRecognitionError(
                f"Whisper decoder ONNX graph at {model_path!r} is missing "
                "the expected 'input_ids'/'position_ids' inputs; cannot "
                "proceed."
            )
        if "attention_mask" not in input_specs:
            raise SpeechRecognitionError(
                f"Whisper decoder ONNX graph at {model_path!r} is missing "
                "the expected 'attention_mask' input; cannot proceed."
            )
        if "logits" not in output_specs:
            raise SpeechRecognitionError(
                f"Whisper decoder ONNX graph at {model_path!r} is missing "
                "the expected 'logits' output; cannot proceed."
            )

        self._self_kv_shapes = {
            name: tuple(
                dim if isinstance(dim, int) else 1
                for dim in input_specs[name].shape
            )
            for name in self._self_kv_in_names
        }
        self._attention_mask_shape = tuple(
            dim if isinstance(dim, int) else self._max_decode_length
            for dim in input_specs["attention_mask"].shape
        )
        self._output_names = list(output_specs.keys())

    def _zero_self_attention_kv(self) -> Tuple[object, ...]:
        np = self._np
        return tuple(
            np.zeros(self._self_kv_shapes[name], dtype=np.float16)
            for name in self._self_kv_in_names
        )

    def _attention_mask_for_step(self, step_index: int) -> object:
        # Matches the sliding-window behavior STEP 9 found in the
        # reference harness's decode loop (app.py): every already-
        # generated position is unmasked (0.0); everything else stays at
        # the large-negative fill.
        np = self._np
        mask = np.full(
            self._attention_mask_shape, _ATTENTION_MASK_NEG_FILL, dtype=np.float16
        )
        visible = min(step_index + 1, mask.shape[-1])
        mask[..., mask.shape[-1] - visible :] = np.float16(0.0)
        return mask

    def run(
        self,
        step_index: int,
        input_token_id: int,
        self_attention_kv: Optional[Tuple[object, ...]],
        cross_attention_kv: Tuple[object, ...],
    ) -> DecoderStepOutput:
        np = self._np
        if self_attention_kv is None:
            self_attention_kv = self._zero_self_attention_kv()

        feed = {
            "input_ids": np.array([[input_token_id]], dtype=np.int32),
            "position_ids": np.array([step_index], dtype=np.int32),
            "attention_mask": self._attention_mask_for_step(step_index),
        }
        for name, tensor in zip(self._self_kv_in_names, self_attention_kv):
            feed[name] = tensor
        for name, tensor in zip(self._cross_kv_names, cross_attention_kv):
            feed[name] = tensor

        try:
            raw_outputs = self._session.run(self._output_names, feed)
        except Exception as exc:
            raise SpeechRecognitionError(
                f"Whisper decoder inference failed at step {step_index}: {exc}"
            ) from exc

        by_name = dict(zip(self._output_names, raw_outputs))
        logits = by_name["logits"]
        updated_self_kv = tuple(by_name[name] for name in self._self_kv_out_names)
        return DecoderStepOutput(logits=logits, self_attention_kv=updated_self_kv)

    def select_next_token(self, logits: object) -> int:
        np = self._np
        return int(np.argmax(np.asarray(logits)))

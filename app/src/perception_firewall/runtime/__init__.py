"""Whisper Snapdragon runtime adapter.

Public entry point: ``WhisperRuntimeAdapter``, a ``SpeechToTextEngine``
implementation for the ONNX Runtime + QNN Execution Provider path STEP 9
investigated. See README.md in this directory for the full architecture,
the optional-dependency strategy, and what remains hardware-dependent.

Importing this package (and every module in it) never imports
``onnxruntime``, ``transformers``, ``qai_hub``, or ``qai_hub_models`` —
those are optional runtime dependencies, imported lazily only when a
concrete session/tokenizer/feature-extractor is actually constructed.
"""

from perception_firewall.runtime.adapter import WhisperRuntimeAdapter
from perception_firewall.runtime.config import (
    WhisperDecodeConfig,
    WhisperModelPaths,
    WhisperRuntimeConfig,
    WhisperTokenizerConfig,
)
from perception_firewall.runtime.platform_guard import (
    DeviceCompatibilityResult,
    PlatformInfo,
    check_snapdragon_windows_host,
)

__all__ = [
    "DeviceCompatibilityResult",
    "PlatformInfo",
    "WhisperDecodeConfig",
    "WhisperModelPaths",
    "WhisperRuntimeAdapter",
    "WhisperRuntimeConfig",
    "WhisperTokenizerConfig",
    "check_snapdragon_windows_host",
]

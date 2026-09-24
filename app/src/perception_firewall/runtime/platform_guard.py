"""Device/host compatibility guard for the Whisper Snapdragon runtime.

STEP 9's investigation found, by direct inspection of the installed
Qualcomm SDK (``qai_hub_models/utils/onnx/torch_wrapper.py``,
function ``_verify_onnxruntime_qnn_installed``), an executable check
gating NPU execution:

    if os.name != "nt" or "Qualcomm" not in platform.processor():
        install_instructions = (
            "NPU execution is supported only on Windows on Snapdragon devices."
        )

This module reimplements that same check independently, with the
platform information injectable, so it is deterministically unit-testable
without needing to actually run on Windows-on-Snapdragon hardware.

IMPORTANT: passing this check does NOT prove NPU execution will succeed,
and does not mean it has ever been exercised. It only establishes that
the host *appears* compatible with the documented runtime path STEP 9
found. Actual validation requires running real inference on real
Windows-on-Snapdragon hardware — see runtime/README.md.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformInfo:
    """Injectable host platform information.

    Mirrors exactly the two values the STEP 9 evidence checks: Python's
    ``os.name`` and ``platform.processor()``. Injectable so tests can
    exercise both the "supported host" and "unsupported host" paths
    deterministically, regardless of what machine the tests actually run
    on.
    """

    os_name: str
    processor: str

    @classmethod
    def from_current_host(cls) -> "PlatformInfo":
        """Read the real host's platform info (``os.name`` /
        ``platform.processor()``)."""
        import os
        import platform as _platform

        return cls(os_name=os.name, processor=_platform.processor())


@dataclass(frozen=True)
class DeviceCompatibilityResult:
    """The result of a compatibility check, with a human-readable reason
    either way — never just a bare boolean."""

    is_compatible: bool
    reason: str


def check_snapdragon_windows_host(
    platform_info: PlatformInfo,
) -> DeviceCompatibilityResult:
    """Check whether ``platform_info`` describes a host compatible with
    the documented Whisper Snapdragon runtime path (Windows + Qualcomm
    processor — see module docstring for the exact evidence).
    """
    if platform_info.os_name != "nt":
        return DeviceCompatibilityResult(
            is_compatible=False,
            reason=(
                "NPU execution requires Windows (os.name == 'nt'); "
                f"detected os.name={platform_info.os_name!r}."
            ),
        )

    if "qualcomm" not in platform_info.processor.lower():
        return DeviceCompatibilityResult(
            is_compatible=False,
            reason=(
                "NPU execution requires a Qualcomm/Snapdragon processor; "
                f"detected processor={platform_info.processor!r}."
            ),
        )

    return DeviceCompatibilityResult(
        is_compatible=True,
        reason=(
            "Host appears compatible with the documented Windows-on-Snapdragon "
            "runtime path (this does not confirm NPU execution has been "
            "validated)."
        ),
    )

import pytest

from perception_firewall.runtime.platform_guard import (
    PlatformInfo,
    check_snapdragon_windows_host,
)


# --- E. unsupported host detection ----------------------------------------------


def test_non_windows_host_is_unsupported():
    info = PlatformInfo(os_name="posix", processor="Qualcomm(R) Snapdragon(R)")
    result = check_snapdragon_windows_host(info)
    assert result.is_compatible is False
    assert "windows" in result.reason.lower()


def test_windows_non_qualcomm_processor_is_unsupported():
    info = PlatformInfo(os_name="nt", processor="Intel64 Family 6 Model 158")
    result = check_snapdragon_windows_host(info)
    assert result.is_compatible is False
    assert "qualcomm" in result.reason.lower()


def test_non_windows_non_qualcomm_is_unsupported():
    info = PlatformInfo(os_name="posix", processor="arm")
    result = check_snapdragon_windows_host(info)
    assert result.is_compatible is False


def test_empty_processor_string_is_unsupported():
    info = PlatformInfo(os_name="nt", processor="")
    result = check_snapdragon_windows_host(info)
    assert result.is_compatible is False


# --- F. supported host detection (injected platform information) ---------------


def test_windows_qualcomm_processor_is_supported():
    info = PlatformInfo(os_name="nt", processor="Qualcomm(R) Snapdragon(R) X Elite")
    result = check_snapdragon_windows_host(info)
    assert result.is_compatible is True


def test_processor_match_is_case_insensitive():
    info = PlatformInfo(os_name="nt", processor="QUALCOMM SNAPDRAGON")
    result = check_snapdragon_windows_host(info)
    assert result.is_compatible is True


def test_reason_never_claims_npu_execution_confirmed():
    info = PlatformInfo(os_name="nt", processor="Qualcomm Snapdragon")
    result = check_snapdragon_windows_host(info)
    assert result.is_compatible is True
    lowered = result.reason.lower()
    assert "does not confirm" in lowered or "not confirm" in lowered


def test_platform_info_from_current_host_returns_platform_info():
    info = PlatformInfo.from_current_host()
    assert isinstance(info, PlatformInfo)
    assert isinstance(info.os_name, str)
    assert isinstance(info.processor, str)

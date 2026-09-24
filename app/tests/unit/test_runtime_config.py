import pytest

from perception_firewall.runtime.config import (
    WhisperDecodeConfig,
    WhisperModelPaths,
    WhisperRuntimeConfig,
    WhisperTokenizerConfig,
)


# --- A. configuration validation (valid cases) --------------------------------


def test_valid_model_paths():
    paths = WhisperModelPaths(encoder_path="enc.onnx", decoder_path="dec.onnx")
    assert paths.encoder_path == "enc.onnx"
    assert paths.decoder_path == "dec.onnx"


def test_valid_tokenizer_config_hf_model_id():
    cfg = WhisperTokenizerConfig(hf_model_id="openai/whisper-base")
    assert cfg.source == "openai/whisper-base"


def test_valid_tokenizer_config_local_path():
    cfg = WhisperTokenizerConfig(local_path="/tmp/whisper-tokenizer")
    assert cfg.source == "/tmp/whisper-tokenizer"


def test_valid_decode_config_default():
    cfg = WhisperDecodeConfig()
    assert cfg.max_decode_length == 200


def test_valid_full_runtime_config():
    config = WhisperRuntimeConfig(
        model_paths=WhisperModelPaths("enc.onnx", "dec.onnx"),
        tokenizer_config=WhisperTokenizerConfig(hf_model_id="openai/whisper-base"),
    )
    assert config.decode_config.max_decode_length == 200


# --- D. invalid configuration ---------------------------------------------------


def test_empty_encoder_path_raises():
    with pytest.raises(ValueError):
        WhisperModelPaths(encoder_path="", decoder_path="dec.onnx")


def test_empty_decoder_path_raises():
    with pytest.raises(ValueError):
        WhisperModelPaths(encoder_path="enc.onnx", decoder_path="")


def test_whitespace_only_encoder_path_raises():
    with pytest.raises(ValueError):
        WhisperModelPaths(encoder_path="   ", decoder_path="dec.onnx")


def test_non_string_encoder_path_raises():
    with pytest.raises(ValueError):
        WhisperModelPaths(encoder_path=123, decoder_path="dec.onnx")


def test_tokenizer_config_requires_exactly_one_source():
    with pytest.raises(ValueError):
        WhisperTokenizerConfig()


def test_tokenizer_config_rejects_both_sources():
    with pytest.raises(ValueError):
        WhisperTokenizerConfig(hf_model_id="openai/whisper-base", local_path="/tmp/x")


def test_decode_config_rejects_zero_max_length():
    with pytest.raises(ValueError):
        WhisperDecodeConfig(max_decode_length=0)


def test_decode_config_rejects_negative_max_length():
    with pytest.raises(ValueError):
        WhisperDecodeConfig(max_decode_length=-1)


def test_runtime_config_rejects_wrong_model_paths_type():
    with pytest.raises(ValueError):
        WhisperRuntimeConfig(
            model_paths="not-a-model-paths-object",  # type: ignore[arg-type]
            tokenizer_config=WhisperTokenizerConfig(hf_model_id="openai/whisper-base"),
        )


def test_runtime_config_rejects_wrong_tokenizer_config_type():
    with pytest.raises(ValueError):
        WhisperRuntimeConfig(
            model_paths=WhisperModelPaths("enc.onnx", "dec.onnx"),
            tokenizer_config="not-a-tokenizer-config",  # type: ignore[arg-type]
        )

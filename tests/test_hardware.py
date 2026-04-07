from unittest.mock import patch

from driftshell.core.hardware import MODEL_31B, MODEL_26B, MODEL_E4B, get_hardware_profile


def _mock_psutil(ram_gb: float):
    class Mem:
        total = int(ram_gb * 1024**3)
    return Mem()


def test_selects_31b_high_ram():
    with patch("psutil.virtual_memory", return_value=_mock_psutil(64)), \
         patch("driftshell.core.hardware._detect_vram_gb", return_value=0.0):
        profile = get_hardware_profile()
    assert profile.selected_model == MODEL_31B


def test_selects_26b_mid_ram():
    with patch("psutil.virtual_memory", return_value=_mock_psutil(16)), \
         patch("driftshell.core.hardware._detect_vram_gb", return_value=0.0):
        profile = get_hardware_profile()
    assert profile.selected_model == MODEL_26B


def test_selects_e4b_low_ram():
    with patch("psutil.virtual_memory", return_value=_mock_psutil(8)), \
         patch("driftshell.core.hardware._detect_vram_gb", return_value=0.0):
        profile = get_hardware_profile()
    assert profile.selected_model == MODEL_E4B


def test_selects_31b_high_vram():
    with patch("psutil.virtual_memory", return_value=_mock_psutil(8)), \
         patch("driftshell.core.hardware._detect_vram_gb", return_value=16.0):
        profile = get_hardware_profile()
    assert profile.selected_model == MODEL_31B

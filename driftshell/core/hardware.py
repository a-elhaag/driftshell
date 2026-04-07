from __future__ import annotations

import functools
import os
import subprocess

import psutil

from driftshell.models.schemas import HardwareProfile

MODEL_31B = "gemma4:31b"
MODEL_26B = "gemma4:26b-moe"
MODEL_E4B = "gemma4:e4b"


def _detect_vram_gb() -> float:
    # Check env override first
    env_override = os.environ.get("DRIFT_VRAM_OVERRIDE")
    if env_override:
        try:
            return float(env_override)
        except ValueError:
            pass

    # Try pynvml (NVIDIA)
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        return info.total / (1024**3)
    except Exception:
        pass

    # Try nvidia-smi subprocess
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return float(result.stdout.strip()) / 1024
    except Exception:
        pass

    # Apple Silicon: unified memory — treat RAM as VRAM
    try:
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType"],
            capture_output=True, text=True, timeout=5
        )
        if "Apple" in result.stdout:
            # Unified memory: report RAM as VRAM so model selection works correctly
            return psutil.virtual_memory().total / (1024**3)
    except Exception:
        pass

    return 0.0


@functools.lru_cache(maxsize=1)
def get_hardware_profile() -> HardwareProfile:
    from driftshell.config.loader import get_config
    cfg = get_config()

    ram_gb = psutil.virtual_memory().total / (1024**3)
    vram_gb = cfg.vram_override if cfg.vram_override is not None else _detect_vram_gb()

    if cfg.model_override:
        model = cfg.model_override
    elif vram_gb >= 16 or ram_gb >= 32:
        model = MODEL_31B
    elif vram_gb >= 8 or ram_gb >= 16:
        model = MODEL_26B
    else:
        model = MODEL_E4B

    return HardwareProfile(vram_gb=vram_gb, ram_gb=ram_gb, selected_model=model)

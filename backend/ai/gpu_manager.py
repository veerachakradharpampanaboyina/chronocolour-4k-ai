"""
ChronoColor 4K AI — GPU Memory Manager

Monitors GPU utilization and manages memory across AI model instances.
Uses pynvml for real-time NVIDIA GPU monitoring.
"""

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


class GPUManager:
    """
    Manages GPU resources for AI model inference.

    Features:
    - Real-time VRAM monitoring via pynvml
    - Multi-GPU device selection
    - Memory-aware model placement
    """

    def __init__(self, device_ids: list[int] | None = None):
        self._device_ids = device_ids or [0]
        self._initialized = False

    def initialize(self) -> None:
        """Initialize NVIDIA Management Library."""
        try:
            import pynvml

            pynvml.nvmlInit()
            self._initialized = True

            device_count = pynvml.nvmlDeviceGetCount()
            logger.info("gpu_manager_initialized", gpu_count=device_count)

            for i in self._device_ids:
                if i < device_count:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle)
                    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    logger.info(
                        "gpu_detected",
                        index=i,
                        name=name,
                        total_mb=round(mem_info.total / (1024 * 1024)),
                        free_mb=round(mem_info.free / (1024 * 1024)),
                    )
        except ImportError:
            logger.warning("pynvml_not_available", msg="GPU monitoring disabled")
        except Exception as e:
            logger.warning("gpu_init_failed", error=str(e))

    def get_free_memory_mb(self, device_id: int = 0) -> int:
        """Get free GPU memory in MB for a specific device."""
        if not self._initialized:
            return 0

        try:
            import pynvml

            handle = pynvml.nvmlDeviceGetHandleByIndex(device_id)
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            return int(mem_info.free / (1024 * 1024))
        except Exception:
            return 0

    def get_total_memory_mb(self, device_id: int = 0) -> int:
        """Get total GPU memory in MB for a specific device."""
        if not self._initialized:
            return 0

        try:
            import pynvml

            handle = pynvml.nvmlDeviceGetHandleByIndex(device_id)
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            return int(mem_info.total / (1024 * 1024))
        except Exception:
            return 0

    def get_utilization(self, device_id: int = 0) -> dict:
        """Get GPU utilization metrics."""
        if not self._initialized:
            return {"gpu_percent": 0, "memory_percent": 0}

        try:
            import pynvml

            handle = pynvml.nvmlDeviceGetHandleByIndex(device_id)
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)

            return {
                "gpu_percent": utilization.gpu,
                "memory_percent": utilization.memory,
                "memory_used_mb": int(mem_info.used / (1024 * 1024)),
                "memory_free_mb": int(mem_info.free / (1024 * 1024)),
                "memory_total_mb": int(mem_info.total / (1024 * 1024)),
            }
        except Exception:
            return {"gpu_percent": 0, "memory_percent": 0}

    def select_best_device(self) -> str:
        """
        Select the GPU device with the most free memory.

        Returns:
            Device string (e.g., 'cuda:0').
        """
        if not self._initialized or not self._device_ids:
            return "cuda:0"

        best_device = 0
        best_free = 0

        for device_id in self._device_ids:
            free = self.get_free_memory_mb(device_id)
            if free > best_free:
                best_free = free
                best_device = device_id

        return f"cuda:{best_device}"

    def cleanup(self) -> None:
        """Cleanup GPU manager resources."""
        if self._initialized:
            try:
                import pynvml
                pynvml.nvmlShutdown()
            except Exception:
                pass
            self._initialized = False


# Global GPU manager instance
gpu_manager = GPUManager()

"""
ChronoColor 4K AI — Base AI Model Interface

Abstract base class that all AI model wrappers must implement.
Provides standardized lifecycle management and inference interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class BaseAIModel(ABC):
    """
    Abstract base for all AI model wrappers in ChronoColor.

    Provides a standardized interface for model loading, unloading,
    and inference. The model registry uses this interface for
    lifecycle management and GPU memory tracking.
    """

    def __init__(self, model_name: str, model_path: str | None = None):
        self.model_name = model_name
        self.model_path = model_path
        self._model: Any = None
        self._device: str = "cpu"
        self._is_loaded: bool = False

    @property
    def is_loaded(self) -> bool:
        """Check if the model is currently loaded in memory."""
        return self._is_loaded

    @property
    def device(self) -> str:
        """Get the device the model is loaded on."""
        return self._device

    @property
    @abstractmethod
    def vram_required_mb(self) -> int:
        """
        Estimated GPU VRAM required for this model in MB.
        Used by the GPU manager for memory planning.
        """
        ...

    @abstractmethod
    def load(self, device: str = "cuda:0") -> None:
        """
        Load model weights into memory.

        Args:
            device: Target device ('cuda:0', 'cuda:1', 'cpu').
        """
        ...

    @abstractmethod
    def unload(self) -> None:
        """Unload model from memory and free GPU resources."""
        ...

    @abstractmethod
    def predict(self, input_data: Any, **kwargs: Any) -> Any:
        """
        Run inference on input data.

        Args:
            input_data: Model-specific input (image, video frames, etc.)
            **kwargs: Additional model-specific parameters.

        Returns:
            Model-specific output.
        """
        ...

    def _set_loaded(self, device: str) -> None:
        """Mark model as loaded on a specific device."""
        self._is_loaded = True
        self._device = device
        logger.info(
            "model_loaded",
            model=self.model_name,
            device=device,
            vram_mb=self.vram_required_mb,
        )

    def _set_unloaded(self) -> None:
        """Mark model as unloaded."""
        self._is_loaded = False
        self._device = "cpu"
        self._model = None
        logger.info("model_unloaded", model=self.model_name)

    def ensure_loaded(self, device: str = "cuda:0") -> None:
        """Load the model if not already loaded."""
        if not self._is_loaded:
            self.load(device)

    def __repr__(self) -> str:
        status = "loaded" if self._is_loaded else "unloaded"
        return f"<{self.__class__.__name__}({self.model_name}, {status}, {self._device})>"

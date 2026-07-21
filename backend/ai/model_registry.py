"""
ChronoColor 4K AI — Model Registry

Singleton registry for lazy loading, caching, and evicting AI models.
Manages GPU memory across multiple models sharing the same GPU.
"""

from __future__ import annotations

import threading
from collections import OrderedDict
from typing import Any, Type

import structlog

from ai.base import BaseAIModel

logger = structlog.get_logger(__name__)


class ModelRegistry:
    """
    Singleton registry managing all AI model instances.

    Features:
    - Lazy loading: models are loaded only when first needed
    - LRU eviction: when GPU memory is low, least-recently-used models are unloaded
    - Thread-safe: uses locks for concurrent access from multiple Celery workers
    """

    _instance: ModelRegistry | None = None
    _lock = threading.Lock()

    def __new__(cls) -> ModelRegistry:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._models: OrderedDict[str, BaseAIModel] = OrderedDict()
        self._model_classes: dict[str, tuple[Type[BaseAIModel], dict]] = {}
        self._model_lock = threading.Lock()
        self._max_vram_mb: int = 20000  # Default 20GB, updated at runtime

    def register(
        self,
        name: str,
        model_class: Type[BaseAIModel],
        **init_kwargs: Any,
    ) -> None:
        """
        Register a model class for lazy instantiation.

        Args:
            name: Unique model name (e.g., 'real_esrgan', 'gfpgan').
            model_class: The BaseAIModel subclass.
            **init_kwargs: Arguments passed to the constructor.
        """
        self._model_classes[name] = (model_class, init_kwargs)
        logger.info("model_registered", name=name, cls=model_class.__name__)

    def get(self, name: str, device: str = "cuda:0") -> BaseAIModel:
        """
        Get a loaded model by name, loading it if necessary.

        Args:
            name: Registered model name.
            device: Target device.

        Returns:
            The loaded model instance.

        Raises:
            KeyError: If model name is not registered.
        """
        with self._model_lock:
            # Return cached model if already loaded
            if name in self._models and self._models[name].is_loaded:
                # Move to end (most recently used)
                self._models.move_to_end(name)
                return self._models[name]

            # Instantiate if not yet created
            if name not in self._models:
                if name not in self._model_classes:
                    raise KeyError(
                        f"Model '{name}' is not registered. "
                        f"Available: {list(self._model_classes.keys())}"
                    )
                cls, kwargs = self._model_classes[name]
                self._models[name] = cls(model_name=name, **kwargs)

            model = self._models[name]

            # Ensure enough VRAM
            self._ensure_vram(model.vram_required_mb, exclude=name)

            # Load the model
            model.load(device)
            self._models.move_to_end(name)
            return model

    def unload(self, name: str) -> None:
        """Unload a specific model from GPU memory."""
        with self._model_lock:
            if name in self._models and self._models[name].is_loaded:
                self._models[name].unload()

    def unload_all(self) -> None:
        """Unload all models from GPU memory."""
        with self._model_lock:
            for model in self._models.values():
                if model.is_loaded:
                    model.unload()

    def get_loaded_models(self) -> list[str]:
        """Get names of all currently loaded models."""
        return [
            name for name, model in self._models.items()
            if model.is_loaded
        ]

    def get_total_vram_used(self) -> int:
        """Get total VRAM used by loaded models in MB."""
        return sum(
            model.vram_required_mb
            for model in self._models.values()
            if model.is_loaded
        )

    def _ensure_vram(self, required_mb: int, exclude: str = "") -> None:
        """
        Ensure enough VRAM is available by evicting LRU models.

        Args:
            required_mb: VRAM needed in MB.
            exclude: Model name to exclude from eviction.
        """
        current_used = self.get_total_vram_used()
        available = self._max_vram_mb - current_used

        if available >= required_mb:
            return

        # Evict least recently used models
        for name in list(self._models.keys()):
            if name == exclude:
                continue
            if not self._models[name].is_loaded:
                continue

            freed = self._models[name].vram_required_mb
            self._models[name].unload()
            available += freed

            logger.info(
                "model_evicted",
                model=name,
                freed_mb=freed,
                available_mb=available,
            )

            if available >= required_mb:
                break

        if available < required_mb:
            logger.warning(
                "insufficient_vram",
                required_mb=required_mb,
                available_mb=available,
            )


# Global registry instance
registry = ModelRegistry()

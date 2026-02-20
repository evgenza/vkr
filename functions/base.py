"""
Базовые классы для функций анализа.

Не используются текущими процедурными функциями (*_my.py),
но предоставляют OOP-паттерн для будущих анализаторов.
См. README.md: 'Добавление новой функции анализа'.
"""
import numpy as np
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AnalysisResult:
    def __init__(self,
                 data: Optional[np.ndarray] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.data = data if data is not None else np.array([])
        self.metadata = metadata if metadata else {}

    def __bool__(self) -> bool:
        return len(self.data) > 0

    def get(self, key: str, default=None):
        return self.metadata.get(key, default)


class BaseAnalyzer(ABC):
    def __init__(self, name: str):
        self.name = name
        self._result: Optional[AnalysisResult] = None

    @abstractmethod
    def analyze(self, data: np.ndarray, **kwargs) -> AnalysisResult:
        pass

    @property
    def result(self) -> Optional[AnalysisResult]:
        return self._result

    def validate_data(self, data: np.ndarray, min_length: int = 10) -> bool:
        if data is None or len(data) == 0:
            logger.error("%s: Пустые данные", self.name)
            return False
        if len(data) < min_length:
            logger.error("%s: Данные слишком короткие (%d < %d)",
                         self.name, len(data), min_length)
            return False
        if not np.all(np.isfinite(data)):
            logger.error("%s: Данные содержат NaN или Inf", self.name)
            return False
        return True

    def _create_result(self, data: np.ndarray, **metadata) -> AnalysisResult:
        return AnalysisResult(data=data, metadata=metadata)

"""
Модель диагностики подшипников: обучение на «здоровых» данных,
определение аномалий в новых сигналах.

Поддерживаемые алгоритмы:
  - Isolation Forest (по умолчанию)
  - One-Class SVM
"""
import logging
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

ALGORITHMS = {
    'iforest': 'Быстрая диагностика (Isolation Forest)',
    'ocsvm': 'Точная диагностика (One-Class SVM)',
}


@dataclass
class DiagnosticResult:
    """Результат диагностики одного файла."""
    labels: np.ndarray           # 1 = норма, -1 = аномалия (для каждого окна)
    scores: np.ndarray           # decision scores (чем ниже — тем хуже)
    anomaly_indices: np.ndarray  # индексы аномальных окон
    total_windows: int = 0
    anomaly_count: int = 0
    anomaly_pct: float = 0.0

    @property
    def is_healthy(self) -> bool:
        return self.anomaly_count == 0

    @property
    def verdict(self) -> str:
        if self.anomaly_pct == 0:
            return "НОРМА ✅"
        elif self.anomaly_pct < 15:
            return "ВНИМАНИЕ ⚠️"
        else:
            return "АНОМАЛИЯ ❌"


class AnomalyModel:
    """Обёртка над sklearn для обучения и диагностики."""

    def __init__(self, algorithm: str = 'iforest', contamination: float = 0.05):
        """
        Parameters
        ----------
        algorithm : str
            'iforest' или 'ocsvm'.
        contamination : float
            Ожидаемая доля аномалий (0..0.5). По умолчанию 5%.
        """
        self.algorithm = algorithm
        self.contamination = contamination
        self._scaler = StandardScaler()
        self._model = None
        self._trained = False
        self._train_files: List[str] = []
        self._train_samples: int = 0

    @property
    def is_trained(self) -> bool:
        return self._trained

    @property
    def info(self) -> str:
        if not self._trained:
            return "Модель не обучена"
        alg = ALGORITHMS.get(self.algorithm, self.algorithm)
        return (f"{alg}, обучено на {len(self._train_files)} файлах "
                f"({self._train_samples} окон)")

    def train(self, X: np.ndarray, file_names: Optional[List[str]] = None):
        """Обучить модель на матрице признаков «здоровых» данных.

        Parameters
        ----------
        X : np.ndarray
            shape (N, 6) — признаки из extract_features().
        file_names : list[str], optional
            Имена файлов (для информации).
        """
        if X.shape[0] < 10:
            raise ValueError(
                f"Недостаточно данных для обучения: {X.shape[0]} окон (нужно >= 10)")

        X_scaled = self._scaler.fit_transform(X)

        if self.algorithm == 'ocsvm':
            self._model = OneClassSVM(kernel='rbf', gamma='scale',
                                       nu=self.contamination)
        else:
            self._model = IsolationForest(
                contamination=self.contamination,
                n_estimators=100, random_state=42)

        self._model.fit(X_scaled)
        self._trained = True
        self._train_files = list(file_names or [])
        self._train_samples = X.shape[0]

        logger.info("Модель обучена: %s, %d окон из %d файлов",
                     ALGORITHMS.get(self.algorithm, self.algorithm),
                     X.shape[0], len(self._train_files))

    def predict(self, X: np.ndarray) -> DiagnosticResult:
        """Диагностировать новые данные.

        Parameters
        ----------
        X : np.ndarray
            shape (N, 6) — признаки нового сигнала.

        Returns
        -------
        DiagnosticResult
        """
        if not self._trained:
            raise RuntimeError("Модель не обучена")

        X_scaled = self._scaler.transform(X)
        labels = self._model.predict(X_scaled)       # 1 = норма, -1 = аномалия
        scores = self._model.decision_function(X_scaled)

        anomaly_idx = np.where(labels == -1)[0]
        total = len(labels)
        count = len(anomaly_idx)
        pct = (count / total * 100) if total > 0 else 0.0

        return DiagnosticResult(
            labels=labels,
            scores=scores,
            anomaly_indices=anomaly_idx,
            total_windows=total,
            anomaly_count=count,
            anomaly_pct=pct,
        )

    def save(self, path: str):
        """Сохранить обученную модель в файл."""
        if not self._trained:
            raise RuntimeError("Модель не обучена — нечего сохранять")

        data = {
            'algorithm': self.algorithm,
            'contamination': self.contamination,
            'scaler': self._scaler,
            'model': self._model,
            'train_files': self._train_files,
            'train_samples': self._train_samples,
        }
        with open(path, 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

        logger.info("Модель сохранена: %s", path)

    @classmethod
    def load(cls, path: str) -> 'AnomalyModel':
        """Загрузить модель из файла."""
        with open(path, 'rb') as f:
            data = pickle.load(f)

        obj = cls(algorithm=data['algorithm'],
                  contamination=data['contamination'])
        obj._scaler = data['scaler']
        obj._model = data['model']
        obj._train_files = data['train_files']
        obj._train_samples = data['train_samples']
        obj._trained = True

        logger.info("Модель загружена: %s", path)
        return obj

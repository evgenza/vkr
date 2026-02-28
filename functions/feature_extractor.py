"""
Извлечение вектора признаков из временного ряда для модели диагностики.

Каждое скользящее окно → вектор из 6 показателей:
  [H (Херст), λ (Ляпунов), DT (фракт. размерность), G (Гёльдер), I (энтропия), Kurt (куртозис)]
"""
import logging

import numpy as np
from scipy.stats import kurtosis

from .Herst_f import Herst_f
from .Lyapunov_f import Lyapunov_f
from .fract_dim_f import fract_dim_f
from .Hoelder_f import Hoelder_f
from .Inform_f import Inform_f
from utils import iter_windows

logger = logging.getLogger(__name__)

# Имена признаков (для заголовков таблиц/CSV)
FEATURE_NAMES = ['H_Херст', 'λ_Ляпунов', 'DT_фракт', 'G_Гёльдер', 'I_энтропия', 'Kurt_куртозис']


def extract_features_single(y: np.ndarray, num_bands: int = 30,
                             deviation: float = 4.0) -> np.ndarray:
    """Извлечь вектор из 6 признаков для одного окна данных.

    Returns
    -------
    np.ndarray
        shape (6,) — [H, λ, DT, G, I, Kurt]
    """
    h = Herst_f(y)
    lyap = Lyapunov_f(y, num_bands, deviation)
    dt_raw = fract_dim_f(y)
    info = Inform_f(y)
    dt = (dt_raw + 2 - h + 1.21 * info) / 3  # интегральная формула
    g = Hoelder_f(y)
    kurt = float(kurtosis(y, fisher=True))

    return np.array([h, lyap, dt, g, info, kurt])


def extract_features(Y: np.ndarray, start_offset: int, window_shift: int,
                     window_width: int, num_windows: int,
                     num_bands: int = 30, deviation: float = 4.0) -> np.ndarray:
    """Извлечь матрицу признаков из временного ряда на скользящих окнах.

    Parameters
    ----------
    Y : np.ndarray
        Входной сигнал.
    start_offset, window_shift, window_width, num_windows
        Параметры скользящего окна.
    num_bands : int
        Число полос (для Ляпунова).
    deviation : float
        Отклонение (для Ляпунова).

    Returns
    -------
    np.ndarray
        shape (N, 6) — по одной строке на каждое окно.
    """
    Y = np.array(Y).flatten()
    rows = []

    for y in iter_windows(Y, start_offset, window_shift, window_width, num_windows):
        row = extract_features_single(y, num_bands, deviation)
        rows.append(row)

    if not rows:
        logger.warning("Не удалось извлечь признаки: нет окон")
        return np.empty((0, 6))

    X = np.array(rows)
    # Заменяем NaN/Inf нулями
    bad = ~np.isfinite(X)
    if np.any(bad):
        logger.warning("Заменено %d NaN/Inf значений в признаках", int(np.sum(bad)))
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

    return X

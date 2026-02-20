"""
Функция Huang для вычисления минимальной разности сингулярных чисел
"""
import numpy as np
from scipy.signal import hilbert
from .exp_smooth_twice import exp_smooth_twice


def Huang_f(y):
    """
    Вычисление минимальной разности логарифмов сингулярных чисел

    Parameters:
    -----------
    y : numpy.ndarray
        Входной ряд данных (столбец)

    Returns:
    --------
    s0 : float
        Минимальная разность логарифмов сингулярных чисел
    """
    y = np.array(y).flatten()
    n = len(y)

    if n < 12:
        return 1.0

    # Сглаживание
    y_sm = exp_smooth_twice(y.reshape(-1, 1), 0.1).flatten()
    yd = y - y_sm

    # Огибающая через преобразование Гильберта (аналог MATLAB envelope)
    analytic_signal = hilbert(yd)
    yh = np.abs(analytic_signal)  # Верхняя огибающая

    from config import config
    l = config.constants.huang_singular_count

    if n < l:
        return 1.0

    # Формирование матрицы (соответствует MATLAB: X(:,j)=yh(j:n-l+j))
    # В MATLAB индексация с 1: j:n-l+j означает элементы с j до n-l+j включительно
    # В Python индексация с 0: j-1:n-l+j-1
    X = np.zeros((n - l + 1, l - 1))
    for j in range(1, l):
        # MATLAB: yh(j:n-l+j) -> Python: yh[j-1:n-l+j]
        X[:, j-1] = yh[j-1:n - l + j]

    # SVD разложение (аналог MATLAB svd(X,0))
    try:
        U, s, Vt = np.linalg.svd(X, full_matrices=False)
        ss = -np.diff(np.log(s + 1e-10))
        s0 = np.min(ss)
    except (np.linalg.LinAlgError, ValueError):
        s0 = 1.0

    return s0


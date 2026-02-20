"""
Информационный показатель
"""
import numpy as np
from scipy.interpolate import interp1d


def Inform_f(y, step=0.1):
    """
    Вычисление информационного показателя

    Parameters:
    -----------
    y : numpy.ndarray
        Входной ряд данных (столбец)
    step : float, optional
        Шаг для интерполяции (по умолчанию 0.1)

    Returns:
    --------
    I : float
        Информационный показатель
    """
    y = np.array(y).flatten()
    n = len(y)

    if n < 2:
        return 0.0

    x0 = np.arange(1, n + 1)
    x = np.arange(0, n + 1, step)

    try:
        f = interp1d(x0, y, kind='quadratic', fill_value='extrapolate')
        ys = f(x)
    except (ValueError, TypeError):
        f = interp1d(x0, y, kind='linear', fill_value='extrapolate')
        ys = f(x)

    # Гистограмма (аналог MATLAB hist)
    H, bins = np.histogram(ys, bins=len(x))
    H = H / np.sum(H)

    # Информационный показатель
    J = np.where(H > 0)[0]
    if len(J) > 0:
        H1 = np.log(H[J])
        I = -np.sum(H[J] * H1) * step
    else:
        I = 0.0

    return I


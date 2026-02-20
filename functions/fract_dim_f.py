"""
Оценивание фрактальной размерности
"""
import numpy as np


def fract_dim_f(y, eps=0.05):
    """
    Вычисление фрактальной размерности

    Parameters:
    -----------
    y : numpy.ndarray
        Входной ряд данных (столбец)
    eps : float, optional
        Порог для поиска близких точек (по умолчанию 0.05)

    Returns:
    --------
    Dt : float
        Фрактальная размерность
    """
    y = np.array(y).flatten()
    L = len(y)

    if L == 0:
        return 0.0

    DT = np.zeros(L)

    for n in range(L):
        y0 = y[n]
        I = np.where(np.abs(y - y0) < eps)[0]
        P = len(I) / (L * 2)

        if P > 0 and eps > 0:
            DT[n] = np.log(P) / np.log(eps)
        else:
            DT[n] = 0.0

    Dt = np.mean(DT)

    return Dt


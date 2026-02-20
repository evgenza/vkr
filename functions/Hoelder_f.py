"""
Оценивание показателя Гёльдера по сплайн-аппроксимации ряда
"""
import numpy as np


def Hoelder_f(y):
    """
    Вычисление показателя Гёльдера

    Parameters:
    -----------
    y : numpy.ndarray
        Входной ряд данных

    Returns:
    --------
    g : float
        Показатель Гёльдера
    """
    y = np.array(y).flatten()
    n = len(y)

    if n < 2:
        return 0.0

    ALP = []

    for k in range(n - 1):
        y0 = y[k]
        alp = []

        for j in range(1, n - k):
            del_x = j
            del_y = abs(y[k + j] - y0)

            if del_x > 0 and del_y > 0:
                log_del_x = np.log(del_x)
                log_del_y = np.log(del_y)
                if log_del_x != 0:
                    alp_val = log_del_y / log_del_x
                    alp.append(alp_val)

        if alp:
            ALP.append(max(alp))

    if ALP:
        g = min(ALP)
    else:
        g = 0.0

    return g


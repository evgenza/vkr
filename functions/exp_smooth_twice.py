"""
Двойное экспоненциальное сглаживание на окне высотой L
"""
import numpy as np


def exp_smooth_twice(Y, alp):
    """
    Двойное экспоненциальное сглаживание
    
    Parameters:
    -----------
    Y : numpy.ndarray
        Входной массив данных (n строк, m столбцов)
    alp : float
        Коэффициент сглаживания
    
    Returns:
    --------
    Y_sm : numpy.ndarray
        Сглаженные данные
    """
    Y = np.array(Y)
    if Y.ndim == 1:
        Y = Y.reshape(-1, 1)
    
    n, m = Y.shape
    
    # Обращение (снизу-вверх)
    Y_rev = np.flipud(Y)
    
    # Экспоненциальный фильтр (снизу-вверх)
    YS = np.zeros_like(Y_rev)
    YS[0, :] = Y_rev[0, :]
    for k in range(1, n):
        YS[k, :] = YS[k-1, :] + alp * (Y_rev[k, :] - YS[k-1, :])
    
    # Обращение отфильтрованных данных (сверху вниз)
    YS_0 = np.flipud(YS)
    
    # Второй проход экспоненциального фильтра
    YSS = np.zeros_like(YS_0)
    YSS[0, :] = YS_0[0, :]
    for k in range(1, n):
        YSS[k, :] = YSS[k-1, :] + alp * (YS_0[k, :] - YSS[k-1, :])
    
    # Корректировка по смещению
    Y_sm = (YS_0 + YSS) / 2
    
    return Y_sm


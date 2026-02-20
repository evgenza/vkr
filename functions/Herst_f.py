"""
Показатель Херста
"""
import numpy as np


def Herst_f(y):
    """
    Вычисление показателя Херста
    
    Parameters:
    -----------
    y : numpy.ndarray
        Входной ряд данных (столбец)
    
    Returns:
    --------
    h : float
        Показатель Херста
    """
    y = np.array(y).flatten()
    z = y - np.mean(y)
    n = len(z)
    s = np.std(z)
    
    if s == 0:
        return 0.5
    
    z1 = np.cumsum(z)
    RM = np.max(z1) - np.min(z1)
    
    if RM == 0 or n <= 1:
        return 0.5
    
    h = (np.log(RM) - np.log(s)) / np.log(n)
    
    return h


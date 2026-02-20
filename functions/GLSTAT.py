"""
Функция GLSTAT для теста Хинича
Альтернативная реализация статистических тестов
"""
import numpy as np
from scipy import stats


def GLSTAT(X, threshold=0.51, n_bins=128):
    """
    Вычисление статистик для теста Хинича
    
    Parameters:
    -----------
    X : numpy.ndarray
        Входной массив данных
    threshold : float
        Пороговое значение
    n_bins : int
        Количество бинов для гистограммы
    
    Returns:
    --------
    sg : numpy.ndarray
        Статистики (включая P_gauss)
    sl : numpy.ndarray
        Дополнительные статистики (включая del_R)
    """
    X = np.array(X).flatten()
    n = len(X)
    
    if n < 3:
        return np.array([0, 0, 0]), np.array([0, 0, 0])
    
    # Нормализация
    X_norm = (X - np.mean(X)) / (np.std(X) + 1e-10)
    
    # Тест на нормальность (Shapiro-Wilk для малых выборок, Jarque-Bera для больших)
    if n < 5000:
        try:
            _, p_value = stats.shapiro(X_norm)
        except (ValueError, TypeError):
            p_value = 0.0
    else:
        try:
            jb_result = stats.jarque_bera(X_norm)
            p_value = float(jb_result.pvalue)
        except (ValueError, TypeError, AttributeError):
            p_value = 0.0
    
    # P_gauss - вероятность того, что данные нормально распределены
    P_gauss = p_value
    
    # Вычисление del_R (размах)
    R = np.max(X) - np.min(X)
    mean_R = np.mean(np.abs(X))
    del_R = abs(R - mean_R)
    
    sg = np.array([0, 0, P_gauss])
    sl = np.array([R, mean_R, del_R])
    
    return sg, sl


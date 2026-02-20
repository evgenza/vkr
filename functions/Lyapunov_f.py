"""
Оценивание показателя Ляпунова
"""
import numpy as np


def Lyapunov_f(y, m, D):
    """
    Вычисление показателя Ляпунова

    Parameters:
    -----------
    y : numpy.ndarray
        Входной ряд данных
    m : int
        Число зон разбиения
    D : float
        Отклонение для контрольных шагов

    Returns:
    --------
    g : float
        Показатель Ляпунова
    """
    y = np.array(y).flatten()
    L = len(y)

    if L < 2:
        return 0.0

    eps = (np.max(y) - np.min(y)) / m

    if eps == 0:
        return 0.0

    nn = list(range(1, round(L/2) + 1, 3))
    V = np.zeros(len(nn))
    TT = np.zeros(len(nn))

    for idx, n in enumerate(nn):
        y0 = y[n-1]  # Индексация с 0 (MATLAB: y(n))
        I = np.where(np.abs(y - y0) < eps)[0]
        P = len(I)

        v = np.zeros(P - 1)
        T = np.zeros(P - 1)

        for k in range(P - 1):
            idx1 = I[k]
            idx2 = I[k + 1]
            diff = idx2 - idx1

            if idx1 + diff < L and idx2 < L:
                z1 = y[idx1:L - diff]
                z2 = y[idx2:L]
                z = np.abs(z1 - z2[:len(z1)])

                JJ = np.where(z > D * eps)[0]

                if len(JJ) > 0:
                    J = np.min(JJ)

                    if J < len(z1) and J < len(z2):
                        u1 = abs(z1[0] - z2[0] + 1)
                        u2 = abs(z1[J] - z2[J] + 1)

                        if u1 != 0 and u2 != 0:
                            v[k] = np.log(u2 + 10) - np.log(u1 + 10)
                            T[k] = J

        V[idx] = np.sum(v)
        TT[idx] = np.sum(T)

    if np.sum(TT) > 0:
        g = np.sum(V) / np.sum(TT)
    else:
        g = 0.0

    return g


"""
Спектрограмма сигнала
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy.signal import spectrogram
from config import config


def specgram_my(Y, fig=None):
    """
    Построение спектрограммы сигнала.

    Returns
    -------
    tuple
        (S, F, T) — спектрограмма, частоты, временные отсчёты
    """
    Y = np.array(Y).flatten()
    n = len(Y)
    s = config.plots.style

    if n < 128:
        nfft = min(64, n)
        nperseg = min(16, n // 2)
        noverlap = min(15, nperseg - 1)
    elif n < 256:
        nfft = min(128, n)
        nperseg = min(32, n // 2)
        noverlap = min(30, nperseg - 1)
    else:
        nfft = 1024
        nperseg = 32
        noverlap = 30

    Fs = 1

    F, T, S = spectrogram(Y, fs=Fs, nperseg=nperseg, noverlap=noverlap, nfft=nfft)

    n_freq = min(64, len(F))
    F1 = F[:n_freq]
    S1 = S[:n_freq, :]

    if fig is None:
        fig = plt.figure(figsize=(12, 8))
        standalone = True
    else:
        fig.clear()
        standalone = False

    ax = fig.add_subplot(111, projection='3d')

    T_mesh, F_mesh = np.meshgrid(T, F1)
    S_abs = np.abs(S1)

    ax.plot_surface(T_mesh, F_mesh, S_abs, cmap=cm.viridis, edgecolor='none')

    ax.set_xlim([0, max(T) if len(T) > 0 else 4000])
    ax.set_ylim([0, max(F1) if len(F1) > 0 else 0.06])
    ax.set_zlim([0, np.max(S_abs) if S_abs.size > 0 else 1])

    ax.set_xlabel('Время (с)',
                  fontsize=s.label_fontsize, fontweight=s.label_fontweight)
    ax.set_ylabel('Частота (Гц)',
                  fontsize=s.label_fontsize, fontweight=s.label_fontweight)
    ax.set_zlabel('СПМ (мВ)',
                  fontsize=s.label_fontsize, fontweight=s.label_fontweight)
    ax.set_title('Спектрограмма',
                 fontsize=s.title_fontsize, fontweight=s.title_fontweight)

    ax.view_init(elev=65, azim=-45)
    ax.grid(True)

    if standalone:
        fig.tight_layout()
        plt.show()

    return S, F, T

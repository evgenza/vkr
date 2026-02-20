"""
Куртозис и пик-фактор
"""
import numpy as np
from utils import setup_figure, finalize_figure, iter_windows
from config import config


def Curth_my(Y, start_offset, window_shift, window_width, num_windows, fig=None):
    Y = np.array(Y).flatten()
    s = config.plots.style

    Curth = []
    V = []

    for y in iter_windows(Y, start_offset, window_shift, window_width, num_windows):
        sig2 = np.cov(y)
        y0 = y - np.mean(y)

        if sig2 > 0:
            curth = np.mean(y0 ** 4) / (sig2 ** 2)
            std_y0 = np.std(y0)
            v = np.max(y0) / std_y0 if std_y0 > 0 else 0
        else:
            curth = 0
            v = 0

        Curth.append(curth)
        V.append(v)

    fig, [ax1, ax2], standalone = setup_figure(fig, 2, 1, figsize=(12, 8))

    ax1.plot(Curth, linewidth=s.thick_linewidth)
    ax1.grid(True)
    ax1.set_title('Фактор куртозиса (динамика эксцесса)',
                  fontsize=s.title_fontsize, fontweight=s.title_fontweight)

    ax2.plot(V, 'k', linewidth=s.thick_linewidth)
    ax2.grid(True)
    ax2.set_title('Динамика пик-фактора',
                  fontsize=s.title_fontsize, fontweight=s.title_fontweight)
    ax2.set_ylabel('Пик-фактор',
                   fontsize=s.label_fontsize, fontweight=s.label_fontweight)
    ax2.set_xlabel('Время (с)',
                   fontsize=s.label_fontsize, fontweight=s.label_fontweight)

    finalize_figure(fig, standalone)


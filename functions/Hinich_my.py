"""
Тест Хинича на заданной системе скользящих окон
"""
import numpy as np
from .GLSTAT import GLSTAT
from utils import setup_figure, finalize_figure, iter_windows
from config import config


def Hinich_my(Y, start_offset, window_shift, window_width, num_windows, fig=None):
    """
    Выполнение теста Хинича на системе скользящих окон.
    """
    Y = np.array(Y).flatten()
    Y1 = np.diff(Y, n=2)
    s = config.plots.style
    c = config.constants

    P_gauss = []
    del_R = []

    for window in iter_windows(Y1, start_offset, window_shift, window_width, num_windows):
        sg, sl = GLSTAT(window, c.hinich_threshold, c.hinich_bins)
        P_gauss.append(sg[2])
        del_R.append(abs(sl[0] - sl[2]))

    actual_windows = len(P_gauss)

    fig, [ax1, ax2], standalone = setup_figure(fig, 2, 1, figsize=(12, 8))

    ax1.bar(range(1, actual_windows + 1), P_gauss, linewidth=2)
    ax1.grid(True)
    ax1.set_title('Тест Хинича',
                  fontsize=s.title_fontsize + 1, fontweight=s.title_fontweight)
    ax1.set_ylabel('P_gauss',
                   fontsize=s.label_fontsize, fontweight=s.label_fontweight)
    ax1.set_xlim([0, actual_windows + 1])
    ax1.set_ylim([0, 1.1])

    ax2.bar(range(1, actual_windows + 1), del_R, linewidth=2)
    ax2.grid(True)
    ax2.set_xlim([0, actual_windows + 1])
    max_val = max(del_R) if del_R else 0
    ax2.set_ylim([0, max_val * 1.1 if max_val > 0 else 5])
    ax2.set_ylabel('del_R',
                   fontsize=s.label_fontsize, fontweight=s.label_fontweight)
    ax2.set_xlabel('Номер скользящего окна',
                   fontsize=s.label_fontsize, fontweight=s.label_fontweight)

    finalize_figure(fig, standalone)


"""
Сегментация - поиск скачков скорости
"""
import numpy as np
from utils import setup_figure, finalize_figure
from config import config


def segment_my(Y, start_offset=1, window_shift=100, window_width=200,
               num_windows=200, fig=None):
    """
    Поиск скачков в данных.

    Returns
    -------
    J : np.ndarray
        Индексы скачков
    """
    Y = np.array(Y).flatten()
    s = config.plots.style
    threshold = config.constants.segment_threshold_mult

    Y1 = np.diff(Y)
    ss = np.std(np.abs(Y1))
    J = np.where(np.abs(Y1) > ss * threshold)[0]

    Y2 = np.zeros_like(Y1)
    Y2[J] = Y1[J]

    fig, [ax], standalone = setup_figure(fig, figsize=(12, 6))

    ax.plot(Y2, linewidth=s.thick_linewidth)
    ax.grid(True)
    ax.set_title('Скачки скорости',
                 fontsize=s.title_fontsize, fontweight=s.title_fontweight)
    ax.set_xlabel('Номер окна', fontsize=s.small_label_fontsize)

    finalize_figure(fig, standalone)
    return J


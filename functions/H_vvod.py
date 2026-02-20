"""
Ввод данных и построение графика временного ряда
"""
import numpy as np
from .exp_smooth_twice import exp_smooth_twice
from utils import setup_figure, finalize_figure
from config import config


def H_vvod(Y, window_width, start_offset, window_shift, num_bands,
           deviation, num_windows, smoothing_alpha, fig=None):
    """
    Ввод данных и построение графика временного ряда с трендом.

    Returns
    -------
    Y_sm : np.ndarray
        Сглаженный временной ряд
    """
    Y = np.array(Y).flatten()
    N = len(Y)
    s = config.plots.style

    Y_sm = exp_smooth_twice(Y.reshape(-1, 1), smoothing_alpha).flatten()

    fig, [ax], standalone = setup_figure(fig, figsize=(12, 6))

    ax.plot(Y, linewidth=s.main_linewidth, label='Временной ряд')
    ax.plot(Y_sm, 'k', linewidth=s.main_linewidth, label='Тренд')
    ax.grid(True)
    ax.set_xlim([0, N])
    ax.set_ylim([np.min(Y), np.max(Y)])
    ax.set_title('Временной ряд данных и его тренд',
                 fontsize=s.title_fontsize, fontweight=s.title_fontweight)
    ax.set_xlabel('Время (с)',
                  fontsize=s.label_fontsize, fontweight=s.label_fontweight)
    ax.set_ylabel('Сигнал (мВ)',
                  fontsize=s.label_fontsize, fontweight=s.label_fontweight)
    ax.legend()

    finalize_figure(fig, standalone)
    return Y_sm


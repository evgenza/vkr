"""
Показатель Гёльдера
"""
import numpy as np
from .Hoelder_f import Hoelder_f
from .exp_smooth_twice import exp_smooth_twice
from utils import setup_figure, finalize_figure, iter_windows
from config import config


def Hoelder_my(Y, num_bands, start_offset, deviation, window_shift,
               window_width, num_windows, fig=None):
    Y = np.array(Y).flatten()
    s = config.plots.style
    alpha = config.smoothing.hoelder

    g = []
    dd = []

    for y in iter_windows(Y, start_offset, window_shift, window_width, num_windows):
        g.append(Hoelder_f(y))
        dd.append(np.max(y) - np.min(y))

    g = np.array(g)
    g_sm = exp_smooth_twice(np.abs(g).reshape(-1, 1), alpha).flatten()

    fig, [ax], standalone = setup_figure(fig, figsize=(12, 6))

    ax.plot(np.abs(g), linewidth=s.main_linewidth, label='Показатель Гёльдера')
    ax.plot(g_sm, 'k', linewidth=s.thick_linewidth, label='Сглаживание')
    ax.grid(True)
    ax.set_title('Показатель Гёльдера',
                 fontsize=s.title_fontsize, fontweight=s.title_fontweight)
    ax.set_xlabel('Номер окна', fontsize=s.small_label_fontsize)
    ax.legend()

    finalize_figure(fig, standalone)


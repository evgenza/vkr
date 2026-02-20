"""
SSA анализ - колебания
"""
import numpy as np
from .Huang_f import Huang_f
from utils import setup_figure, finalize_figure, iter_windows
from config import config


def SSA_my(Y, start_offset, window_shift, window_width, num_windows, fig=None):
    Y = np.array(Y).flatten()
    s = config.plots.style
    ssa_threshold = config.constants.ssa_threshold

    s0 = []
    y_h = []

    for y in iter_windows(Y, start_offset, window_shift, window_width, num_windows):
        s0.append(Huang_f(y))
        y_d = np.diff(y, n=1)
        y_h.append(np.max(y_d) - np.min(y_d) if len(y_d) > 0 else 0)

    s0 = np.array(s0)
    y_h = np.array(y_h)

    Js = np.where(s0 < ssa_threshold)[0]
    ss = np.zeros_like(s0)
    if len(Js) > 0 and len(y_h) > 0:
        ss[Js] = np.mean(y_h)

    fig, [ax1, ax2], standalone = setup_figure(fig, 2, 1, figsize=(12, 8))

    ax1.plot(y_h, linewidth=s.thick_linewidth, label='Размах разностей')
    ax1.plot(ss, 'r', linewidth=s.thick_linewidth, label='Участки с малыми разностями')
    ax1.grid(True)
    ax1.legend()

    ax2.plot(s0, linewidth=s.thick_linewidth)
    ax2.grid(True)
    ax2.set_title('Разности логарифмов сингулярных чисел',
                  fontsize=s.title_fontsize)
    ax2.set_xlabel('Время (с)', fontsize=s.label_fontsize)

    finalize_figure(fig, standalone)


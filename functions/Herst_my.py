"""
Показатели Херста и Ляпунова
"""
import numpy as np
from .Herst_f import Herst_f
from .fract_dim_f import fract_dim_f
from .Inform_f import Inform_f
from .Lyapunov_f import Lyapunov_f
from .exp_smooth_twice import exp_smooth_twice
from utils import setup_figure, finalize_figure, iter_windows
from config import config


def Herst_my(Y, num_bands, start_offset, window_shift, deviation,
             window_width, num_windows, fig=None):
    """
    Вычисление показателей Херста, эмерджентности, фрактальной размерности и Ляпунова.
    """
    Y = np.array(Y).flatten()
    s = config.plots.style
    alpha = config.smoothing.herst

    H = []
    I = []
    DT = []
    Lyap = []

    for y in iter_windows(Y, start_offset, window_shift, window_width, num_windows):
        h = Herst_f(y)
        H.append(h)

        Ii = Inform_f(y)
        I.append(Ii)

        Dt = fract_dim_f(y)
        DT.append((Dt + 4 - h + 1.21 * Ii) / 3)

        Lyap.append(Lyapunov_f(y, num_bands, deviation))

    H = np.array(H)
    I = np.array(I)
    DT = np.array(DT)
    Lyap = np.array(Lyap)

    H_sm = exp_smooth_twice(H.reshape(-1, 1), alpha).flatten()
    DT_sm = exp_smooth_twice(DT.reshape(-1, 1), alpha).flatten()
    I_sm = exp_smooth_twice(I.reshape(-1, 1), alpha).flatten()
    Lyap_sm = exp_smooth_twice(Lyap.reshape(-1, 1), alpha).flatten()

    fig, [ax1, ax2], standalone = setup_figure(fig, 2, 1, figsize=(12, 10))

    lw = s.thick_linewidth
    ax1.plot(H, linewidth=lw, label='Показатель Херста')
    ax1.plot(I, 'm', linewidth=lw, label='Эмерджентность')
    ax1.plot(DT, 'g', linewidth=lw, label='Фрактальная размерность')
    ax1.plot(DT_sm, 'k', linewidth=lw, label='Сглаживание')
    ax1.plot(H_sm, 'k', linewidth=lw)
    ax1.plot(I_sm, 'k', linewidth=lw)
    ax1.grid(True)
    ax1.legend()
    ax1.set_title('Показатель Херста, эмерджентность и фрактальная размерность',
                  fontsize=s.title_fontsize, fontweight=s.title_fontweight)

    ax2.plot(Lyap, 'b', linewidth=lw, label='Показатель Ляпунова')
    ax2.plot(Lyap_sm, 'k', linewidth=lw, label='Сглаживание')
    ax2.grid(True)
    ax2.legend()
    ax2.set_title('Старший показатель Ляпунова',
                  fontsize=s.title_fontsize, fontweight=s.title_fontweight)
    ax2.set_xlabel('Номер окна',
                   fontsize=s.label_fontsize, fontweight=s.label_fontweight)

    finalize_figure(fig, standalone)


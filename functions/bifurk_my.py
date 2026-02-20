"""
Вывод участков перед k-м скачком на фазовые плоскости
"""
import logging
import numpy as np
from .Herst_f import Herst_f
from .fract_dim_f import fract_dim_f
from .Inform_f import Inform_f
from .Hoelder_f import Hoelder_f
from .Lyapunov_f import Lyapunov_f
from .exp_smooth_twice import exp_smooth_twice
from utils import setup_figure, finalize_figure
from config import config

logger = logging.getLogger(__name__)


def bifurk_my(Y, num_bands, deviation, L0, L1, J, jump_number, fig=None):
    """
    Анализ участков перед k-м скачком.

    Returns
    -------
    tuple
        (DT, H, G) — фрактальная размерность, показатель Гёльдера, показатель Ляпунова
    """
    Y = np.array(Y).flatten()
    J = np.array(J)
    s = config.plots.style
    alpha = config.smoothing.bifurcation

    if len(J) == 0 or jump_number < 1 or jump_number > len(J):
        logger.error("Некорректный номер скачка %d (всего скачков: %d)", jump_number, len(J))
        return np.array([]), np.array([]), np.array([])

    u = J[jump_number - 1]

    DT = []
    H = []
    G = []

    # MATLAB: for j=1:L0+L1; Y(u-L0-L1+j : u-L0+j-1)
    for j in range(1, L0 + L1 + 1):
        start_idx = u - L0 - L1 + j - 1
        end_idx = u - L0 + j - 1

        if start_idx >= 0 and end_idx < len(Y) and start_idx < end_idx:
            YY = Y[start_idx:end_idx]
            if len(YY) > 0:
                h_val = Herst_f(YY)
                I_val = Inform_f(YY)
                Dt_val = fract_dim_f(YY)
                DT.append((Dt_val + 4 - h_val + 1.21 * I_val) / 3)
                H.append(Hoelder_f(YY))
                G.append(Lyapunov_f(YY, num_bands, deviation))
            else:
                DT.append(0)
                H.append(0)
                G.append(0)
        else:
            DT.append(0)
            H.append(0)
            G.append(0)

    DT = np.array(DT)
    H = np.array(H)
    G = np.array(G)

    fig, [ax1, ax2], standalone = setup_figure(fig, 1, 2, figsize=(14, 6))

    ms = s.marker_size
    lw = s.thick_linewidth + 1
    if len(H) >= L0 + L1:
        ax1.plot(H[:L0], DT[:L0], '*b', markersize=ms, linewidth=lw, label='До скачка')
        ax1.plot(H[L0:L0+L1], DT[L0:L0+L1], '*r', markersize=ms, linewidth=lw, label='После скачка')
    ax1.grid(True)
    ax1.set_xlabel('Показатель Гёльдера',
                   fontsize=s.small_label_fontsize, fontweight=s.label_fontweight)
    ax1.set_ylabel('Фрактальная размерность',
                   fontsize=s.small_label_fontsize, fontweight=s.label_fontweight)
    ax1.set_title('Последние участки перед n-м скачком',
                  fontsize=s.small_label_fontsize, fontweight=s.title_fontweight)
    ax1.legend()

    if len(H) >= L0 + L1:
        ax2.plot(H[:L0], G[:L0], '*b', markersize=ms, linewidth=lw, label='До скачка')
        ax2.plot(H[L0:L0+L1], G[L0:L0+L1], '*r', markersize=ms, linewidth=lw, label='После скачка')
    ax2.grid(True)
    ax2.set_xlabel('Показатель Гёльдера',
                   fontsize=s.small_label_fontsize, fontweight=s.label_fontweight)
    ax2.set_ylabel('Старший показатель Ляпунова',
                   fontsize=s.small_label_fontsize, fontweight=s.label_fontweight)
    ax2.set_title('Последние участки перед n-м скачком',
                  fontsize=s.small_label_fontsize, fontweight=s.title_fontweight)
    ax2.legend()

    finalize_figure(fig, standalone)
    return DT, H, G


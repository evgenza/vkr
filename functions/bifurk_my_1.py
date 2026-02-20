"""
Кумулятивные суммы
"""
import logging
import numpy as np
from utils import setup_figure, finalize_figure
from config import config

logger = logging.getLogger(__name__)


def bifurk_my_1(DT, H, G, L0, L1, fig=None):
    DT = np.array(DT).flatten()
    H = np.array(H).flatten()
    G = np.array(G).flatten()

    if len(DT) < L0 + L1 or len(H) < L0 + L1 or len(G) < L0 + L1:
        logger.error("Недостаточно данных для кумулятивных сумм")
        return

    s = config.plots.style
    c = config.constants

    DT1 = DT - np.mean(DT[:L0])
    sDT = np.std(DT)

    H1 = H - np.mean(H[:L0])
    sH = np.std(H)

    G1 = G - np.mean(G[:L0])
    sG = np.std(G)

    fig, [ax1, ax2, ax3], standalone = setup_figure(fig, 1, 3, figsize=(16, 5))

    lw = s.thick_linewidth
    x_range = [1, L0 + L1]
    fs = s.small_label_fontsize
    fw = s.label_fontweight

    ax1.plot(np.cumsum(DT1), linewidth=lw)
    ax1.plot(x_range, [c.cumsum_dt_multiplier * sH] * 2, 'k', linewidth=lw)
    ax1.plot(x_range, [-c.cumsum_dt_multiplier * sH] * 2, 'k', linewidth=lw)
    ax1.grid(True)
    ax1.set_title('Кумулятивные суммы', fontsize=fs, fontweight=s.title_fontweight)
    ax1.set_ylabel('Фрактальная размерность', fontsize=fs, fontweight=fw)
    ax1.set_xlabel('Окно перед скачком', fontsize=fs, fontweight=fw)

    lw5 = lw + 1
    ax2.plot(np.cumsum(H1), linewidth=lw5)
    ax2.plot(x_range, [c.cumsum_h_multiplier * sDT] * 2, 'k', linewidth=lw5)
    ax2.plot(x_range, [-c.cumsum_h_multiplier * sDT] * 2, 'k', linewidth=lw5)
    ax2.grid(True)
    ax2.set_title('Кумулятивные суммы', fontsize=fs, fontweight=s.title_fontweight)
    ax2.set_ylabel('Показатель Гёльдера', fontsize=fs, fontweight=fw)
    ax2.set_xlabel('Окно перед скачком', fontsize=fs, fontweight=fw)

    ax3.plot(np.cumsum(G1), linewidth=lw5)
    ax3.plot(x_range, [c.cumsum_g_multiplier * sG] * 2, 'k', linewidth=lw5)
    ax3.plot(x_range, [-c.cumsum_g_multiplier * sG] * 2, 'k', linewidth=lw5)
    ax3.grid(True)
    ax3.set_title('Кумулятивные суммы', fontsize=fs, fontweight=s.title_fontweight)
    ax3.set_ylabel('Показатель Ляпунова', fontsize=fs, fontweight=fw)
    ax3.set_xlabel('Окно перед скачком', fontsize=fs, fontweight=fw)

    finalize_figure(fig, standalone)


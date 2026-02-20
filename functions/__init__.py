from .base import BaseAnalyzer, AnalysisResult

from .H_vvod import H_vvod
from .Hinich_my import Hinich_my
from .Herst_my import Herst_my
from .Hoelder_my import Hoelder_my
from .segment_my import segment_my
from .Curth_my import Curth_my
from .bifurk_my import bifurk_my
from .bifurk_my_1 import bifurk_my_1
from .SSA_my import SSA_my
from .specgram_my import specgram_my

__all__ = [
    'BaseAnalyzer',
    'AnalysisResult',
    'H_vvod',
    'Hinich_my',
    'Herst_my',
    'Hoelder_my',
    'segment_my',
    'Curth_my',
    'bifurk_my',
    'bifurk_my_1',
    'SSA_my',
    'specgram_my',
]
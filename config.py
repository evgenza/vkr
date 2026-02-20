"""
Конфигурация приложения

Централизованное хранилище настроек и констант
"""
from dataclasses import dataclass, field
from typing import List, Tuple, NamedTuple


class AnalysisParams(NamedTuple):
    """Параметры анализа с понятными именами"""
    window_width: int       # Ширина окна
    start_offset: int       # Начало отсчёта
    window_shift: int       # Сдвиг окна
    num_bands: int          # Число полос
    deviation: float        # Отклонение
    num_windows: int        # Число окон
    smoothing_alpha: float  # Коэффициент сглаживания
    jump_number: int        # Номер скачка


@dataclass
class DefaultParameters:
    """Параметры по умолчанию"""
    # Параметры скользящего окна
    window_width: int = 200     # Ширина окна
    start_offset: int = 1       # Начало отсчёта
    window_shift: int = 100     # Сдвиг окна
    num_bands: int = 30         # Число полос
    deviation: float = 4.0      # Отклонение
    num_windows: int = 200      # Число окон
    smoothing_alpha: float = 0.01  # Коэффициент сглаживания
    
    # Параметры скачка
    jump_number: int = 1        # Номер скачка
    
    # Параметры бифуркации
    L0: int = 100               # Длина первого участка
    L1: int = 100               # Длина второго участка
    
    @property
    def as_tuple(self) -> AnalysisParams:
        """Получить как именованный кортеж"""
        return AnalysisParams(
            window_width=self.window_width,
            start_offset=self.start_offset,
            window_shift=self.window_shift,
            num_bands=self.num_bands,
            deviation=self.deviation,
            num_windows=self.num_windows,
            smoothing_alpha=self.smoothing_alpha,
            jump_number=self.jump_number
        )


@dataclass
class ValidationRules:
    """Правила валидации параметров"""
    window_width: Tuple[int, int, int] = field(default=(1, 10000, 10))
    start_offset: Tuple[int, int, int] = field(default=(0, 1000, 1))
    window_shift: Tuple[int, int, int] = field(default=(1, 1000, 100))
    num_bands: Tuple[int, int, int] = field(default=(1, 500, 30))
    deviation: Tuple[float, float, float] = field(default=(0.1, 100.0, 4.0))
    num_windows: Tuple[int, int, int] = field(default=(1, 1000, 200))
    smoothing_alpha: Tuple[float, float, float] = field(default=(0.001, 1.0, 0.01))
    jump_number: Tuple[int, int, int] = field(default=(1, 100, 1))


@dataclass
class SmoothingConfig:
    """Коэффициенты сглаживания для различных анализов"""
    herst: float = 0.4
    hoelder: float = 0.2
    bifurcation: float = 0.1
    input_data: float = 0.01


@dataclass
class AnalysisConstants:
    """Константы, используемые в функциях анализа"""
    # Сегментация
    segment_threshold_mult: float = 12.0

    # Хуанг / SSA
    huang_singular_count: int = 12
    huang_smoothing_alpha: float = 0.1
    ssa_threshold: float = 0.005

    # Кумулятивные суммы
    cumsum_dt_multiplier: float = 20.0
    cumsum_h_multiplier: float = 200.0
    cumsum_g_multiplier: float = 25.0

    # Хинич
    hinich_threshold: float = 0.51
    hinich_bins: int = 128


@dataclass
class PlotStyle:
    """Настройки стиля графиков"""
    title_fontsize: int = 14
    label_fontsize: int = 14
    small_label_fontsize: int = 12
    title_fontweight: str = 'bold'
    label_fontweight: str = 'bold'
    main_linewidth: int = 3
    thick_linewidth: int = 4
    marker_size: int = 8


@dataclass
class PlotSettings:
    """Настройки графиков"""
    figsize_main: Tuple[int, int] = (12, 8)
    figsize_wide: Tuple[int, int] = (14, 10)
    figsize_large: Tuple[int, int] = (16, 5)
    dpi: int = 100
    grid: bool = True
    linewidth: int = 3
    style: PlotStyle = field(default_factory=PlotStyle)


@dataclass
class FileFormats:
    """Поддерживаемые форматы файлов"""
    DATA: List[str] = field(default_factory=lambda: [
        '.mat', '.txt', '.csv', '.wav'
    ])
    FILTER: str = (
        "Data Files (*.mat *.txt *.csv *.wav);;"
        "Text Files (*.txt);;"
        "CSV Files (*.csv);;"
        "MATLAB Files (*.mat);;"
        "Audio Files (*.wav);;"
        "All Files (*)"
    )


@dataclass
class AppConfig:
    """Основная конфигурация приложения"""
    title: str = "Характеристики нелинейности и хаотичности"
    subtitle: str = (
        "Оценивание показателей нелинейности и хаотичности "
        "временного ряда на R скользящих окнах шириной L со сдвигом d"
    )
    min_width: int = 1000
    min_height: int = 700
    default_width: int = 1200
    default_height: int = 800
    
    parameters: DefaultParameters = field(default_factory=DefaultParameters)
    validation: ValidationRules = field(default_factory=ValidationRules)
    plots: PlotSettings = field(default_factory=PlotSettings)
    files: FileFormats = field(default_factory=FileFormats)
    smoothing: SmoothingConfig = field(default_factory=SmoothingConfig)
    constants: AnalysisConstants = field(default_factory=AnalysisConstants)


# Глобальный экземпляр конфигурации
config = AppConfig()


def get_analysis_params() -> AnalysisParams:
    """Получить параметры с понятными именами"""
    return config.parameters.as_tuple


def get_default_parameters() -> DefaultParameters:
    """Получить параметры по умолчанию"""
    return config.parameters

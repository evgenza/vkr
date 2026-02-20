"""
Утилиты для проекта

Общие вспомогательные функции
"""
import logging
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional, Tuple, Union, List, Generator
from matplotlib.figure import Figure
from matplotlib.axes import Axes

logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    """
    Настройка логгирования

    Parameters
    ----------
    level : int
        Уровень логгирования
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def validate_array(data: np.ndarray, min_length: int = 10) -> bool:
    """
    Проверка массива данных

    Parameters
    ----------
    data : np.ndarray
        Массив для проверки
    min_length : int
        Минимальная длина массива

    Returns
    -------
    bool
        True если массив валиден
    """
    if data is None:
        return False
    if not isinstance(data, np.ndarray):
        return False
    if len(data) < min_length:
        return False
    if not np.all(np.isfinite(data)):
        return False
    return True


def normalize_array(data: np.ndarray) -> np.ndarray:
    """
    Нормализация массива (z-score)

    Parameters
    ----------
    data : np.ndarray
        Массив для нормализации

    Returns
    -------
    np.ndarray
        Нормализованный массив
    """
    mean = np.mean(data)
    std = np.std(data)
    if std == 0:
        return data - mean
    return (data - mean) / std


def detect_outliers_iqr(data: np.ndarray, k: float = 1.5) -> np.ndarray:
    """
    Обнаружение выбросов методом IQR

    Parameters
    ----------
    data : np.ndarray
        Массив данных
    k : float
        Коэффициент для IQR

    Returns
    -------
    np.ndarray
        Индексы выбросов
    """
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    lower_bound = q1 - k * iqr
    upper_bound = q3 + k * iqr
    return np.where((data < lower_bound) | (data > upper_bound))[0]


def safe_divide(numerator: Union[float, np.ndarray],
                denominator: Union[float, np.ndarray],
                default: float = 0.0) -> Union[float, np.ndarray]:
    """
    Безопасное деление с обработкой деления на ноль

    Parameters
    ----------
    numerator : float | np.ndarray
        Числитель
    denominator : float | np.ndarray
        Знаменатель
    default : float
        Значение по умолчанию при делении на ноль

    Returns
    -------
    float | np.ndarray
        Результат деления
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        result = np.divide(numerator, denominator)
        if isinstance(result, np.ndarray):
            result = np.nan_to_num(result, nan=default, posinf=default, neginf=default)
        elif not np.isfinite(result):
            result = default
    return result


def load_data_file(file_path: str) -> Optional[np.ndarray]:
    """
    Загрузка данных из файла

    Parameters
    ----------
    file_path : str
        Путь к файлу

    Returns
    -------
    np.ndarray | None
        Загруженные данные или None при ошибке
    """
    path = Path(file_path)
    if not path.exists():
        logger.error(f"Файл не найден: {file_path}")
        return None

    try:
        suffix = path.suffix.lower()

        if suffix == '.mat':
            from scipy.io import loadmat
            data = loadmat(file_path)
            # Поиск переменной Y или первой числовой
            if 'Y' in data:
                return data['Y'].flatten()
            keys = [k for k in data.keys() if not k.startswith('__')]
            if keys:
                return data[keys[0]].flatten()
            logger.error("Не найдена переменная Y в .mat файле")
            return None

        elif suffix in ['.txt', '.csv']:
            return np.loadtxt(file_path).flatten()

        elif suffix == '.wav':
            from scipy.io import wavfile
            _, data = wavfile.read(file_path)
            return data.flatten()

        else:
            # Попытка загрузить как текст
            return np.loadtxt(file_path).flatten()

    except Exception as e:
        logger.error(f"Ошибка загрузки файла {file_path}: {e}")
        return None


def get_signal_properties(data: np.ndarray) -> dict:
    """
    Получение основных свойств сигнала

    Parameters
    ----------
    data : np.ndarray
        Сигнал

    Returns
    -------
    dict
        Свойства сигнала
    """
    return {
        'length': len(data),
        'min': float(np.min(data)),
        'max': float(np.max(data)),
        'mean': float(np.mean(data)),
        'std': float(np.std(data)),
        'var': float(np.var(data)),
        'skew': float(_safe_skew(data)),
        'kurtosis': float(_safe_kurtosis(data)),
    }


def _safe_skew(data: np.ndarray) -> float:
    """Безопасное вычисление асимметрии"""
    try:
        from scipy.stats import skew
        return float(skew(data))
    except (ImportError, ValueError, FloatingPointError):
        return 0.0


def _safe_kurtosis(data: np.ndarray) -> float:
    """Безопасное вычисление эксцесса"""
    try:
        from scipy.stats import kurtosis
        return float(kurtosis(data))
    except (ImportError, ValueError, FloatingPointError):
        return 0.0


def estimate_sampling_rate(data_length: int,
                           duration_hint: Optional[float] = None) -> float:
    """
    Оценка частоты дискретизации

    Parameters
    ----------
    data_length : int
        Длина данных
    duration_hint : float, optional
        Подсказка о длительности сигнала

    Returns
    -------
    float
        Оценка частоты дискретизации
    """
    if duration_hint:
        return data_length / duration_hint
    return data_length / 100.0


def iter_windows(data: np.ndarray,
                 start_offset: int,
                 window_shift: int,
                 window_width: int,
                 num_windows: int) -> Generator[np.ndarray, None, None]:
    """
    Генератор скользящих окон по данным.

    Parameters
    ----------
    data : np.ndarray
        Входные данные
    start_offset : int
        Начало отсчёта
    window_shift : int
        Сдвиг окна
    window_width : int
        Ширина окна
    num_windows : int
        Максимальное число окон

    Yields
    ------
    np.ndarray
        Окно данных длины window_width
    """
    for k in range(num_windows):
        start_idx = start_offset + k * window_shift
        end_idx = start_idx + window_width
        if end_idx <= len(data):
            yield data[start_idx:end_idx]
        else:
            break


def setup_figure(fig: Optional[Figure],
                 nrows: int = 1,
                 ncols: int = 1,
                 figsize: Tuple[int, int] = (12, 8)
                 ) -> Tuple[Figure, List[Axes], bool]:
    """
    Создание фигуры и осей — единый интерфейс для standalone и embedded режимов.

    Returns
    -------
    tuple
        (fig, axes_list, standalone)
    """
    if fig is None:
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize, squeeze=False)
        standalone = True
        axes = axes.flatten().tolist()
    else:
        axes = [fig.add_subplot(nrows, ncols, i + 1)
                for i in range(nrows * ncols)]
        standalone = False
    return fig, axes, standalone


def finalize_figure(fig: Figure, standalone: bool) -> None:
    """Завершение отрисовки: tight_layout + show для standalone."""
    if standalone:
        fig.tight_layout()
        plt.show()

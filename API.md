# API Документация

## Конфигурация (config.py)

### Классы конфигурации

#### `AppConfig`
Основной класс конфигурации приложения.

```python
from config import config

# Доступ к настройкам
title = config.title  # "Характеристики нелинейности и хаотичности"
min_size = (config.min_width, config.min_height)
```

#### `DefaultParameters`
Параметры по умолчанию.

```python
from config import config

L = config.parameters.L      # 200 - ширина окна
d = config.parameters.d      # 100 - сдвиг окна
R = config.parameters.R      # 200 - число окон
```

#### `ValidationRules`
Правила валидации параметров.

```python
from config import config

rules = config.validation
L_min, L_max, L_default = rules.L  # (1, 10000, 10)
```

#### `get_default_parameters()`
Получить параметры как словарь.

```python
from config import get_default_parameters

params = get_default_parameters()
# {'L': 200, 'K': 1, 'd': 100, 'm': 30, 'D': 4.0, 'R': 200, 'alp': 0.01, 'n': 1}
```

---

## Утилиты (utils.py)

### Загрузка данных

#### `load_data_file(file_path: str) -> Optional[np.ndarray]`
Загрузка данных из файла.

```python
from utils import load_data_file

data = load_data_file('test_sinusoid.txt')
if data is not None:
    print(f"Загружено {len(data)} отсчётов")
```

### Валидация

#### `validate_array(data: np.ndarray, min_length: int = 10) -> bool`
Проверка массива данных.

```python
from utils import validate_array

if validate_array(data, min_length=100):
    print("Данные валидны")
```

### Нормализация

#### `normalize_array(data: np.ndarray) -> np.ndarray`
Z-score нормализация.

```python
from utils import normalize_array

data_norm = normalize_array(data)
```

### Свойства сигнала

#### `get_signal_properties(data: np.ndarray) -> dict`
Получение статистик сигнала.

```python
from utils import get_signal_properties

props = get_signal_properties(data)
# {
#     'length': 1000,
#     'min': -2.5,
#     'max': 3.1,
#     'mean': 0.1,
#     'std': 1.0,
#     'skew': 0.05,
#     'kurtosis': 2.9
# }
```

### Логгирование

#### `setup_logging(level: int = logging.INFO)`
Настройка логгирования.

```python
from utils import setup_logging
import logging

setup_logging(logging.DEBUG)
```

---

## Базовые классы (functions/base.py)

### `BaseAnalyzer`
Базовый класс для всех анализаторов.

```python
from functions.base import BaseAnalyzer, AnalysisResult

class MyAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("MyAnalyzer")
    
    def analyze(self, data, **kwargs) -> AnalysisResult:
        if not self.validate_data(data):
            return AnalysisResult()
        
        result = self._compute(data)
        return self._create_result(data=result, metric="value")
```

### `WindowedAnalyzer`
Анализатор со скользящими окнами.

```python
from functions.base import WindowedAnalyzer

class WindowedMyAnalyzer(WindowedAnalyzer):
    def analyze(self, data, L=200, d=100, R=100, **kwargs):
        windows = self.extract_windows(data, K=1, d=d, L=L, R=R)
        
        results = []
        for window in windows:
            results.append(self._process(window))
        
        return self._create_result(data=np.array(results))
```

### `AnalysisResult`
Результат анализа.

```python
result = analyzer.analyze(data)

if result:  # Проверка на успешность
    data = result.data
    metadata = result.metadata
    custom_value = result.get('metric_name')
```

---

## Ядро анализа (functions/core.py)

### `ChaosAnalyzer`
Вычисление всех метрик хаотичности.

```python
from functions.core import ChaosAnalyzer

analyzer = ChaosAnalyzer()
result = analyzer.analyze(
    data,
    m=30,      # число полос
    K=1,       # начало отсчёта
    d=100,     # сдвиг
    D=4.0,     # отклонение
    L=200,     # ширина окна
    R=200,     # число окон
    smooth_alpha=0.4  # сглаживание
)

# Доступ к метрикам
hurst = analyzer.get_hurst()
lyapunov = analyzer.get_lyapunov()

# Или из результата
hurst = result.get('hurst')
lyapunov_smoothed = result.get('lyapunov_smoothed')
```

### `HoelderAnalyzer`
Показатель Гёльдера.

```python
from functions.core import HoelderAnalyzer

analyzer = HoelderAnalyzer()
result = analyzer.analyze(data, K=1, d=100, L=200, R=200)

hoelder = result.data  # Значения показателя
hoelder_sm = result.get('hoelder_smoothed')
```

### `ChaosMetrics`
Структура для хранения метрик.

```python
from functions.core import ChaosMetrics

metrics = ChaosMetrics(
    hurst=H,
    lyapunov=Lyap,
    fractal_dim=DT,
    emergent=I,
    hoelder=G
)
```

---

## Загрузка данных (functions/data_loader.py)

### `DataLoader`
Загрузчик файлов.

```python
from functions.data_loader import DataLoader

loader = DataLoader()

# Загрузка
data = loader.load('test.txt')

# Валидация
valid, message = loader.validate(data, min_length=100)
if not valid:
    print(f"Ошибка: {message}")
```

### `DataPreprocessor`
Предобработка данных.

```python
from functions.data_loader import DataPreprocessor

preprocessor = DataPreprocessor(smooth_alpha=0.01)

# Сглаживание
smoothed = preprocessor.smooth(data)

# Удаление тренда
detrended = preprocessor.detrend(data, smooth=True)

# Нормализация
normalized = preprocessor.normalize(data, method='zscore')
```

### `DataAnalyzer`
Комплексный анализ данных.

```python
from functions.data_loader import DataAnalyzer

analyzer = DataAnalyzer(smooth_alpha=0.01)
result = analyzer.load_and_analyze('test.txt', smooth=True)

# Доступ к данным
raw = analyzer.raw_data
smoothed = analyzer.smoothed_data
props = analyzer.properties  # Статистики
```

---

## Традиционные функции

Все оригинальные функции доступны для обратной совместимости:

```python
from functions import (
    H_vvod,           # Ввод данных
    Hinich_my,        # Тест Хинича
    Herst_my,         # Херст и Ляпунов
    Hoelder_my,       # Гёльдер
    segment_my,       # Сегментация
    Curth_my,         # Куртозис
    bifurk_my,        # Бифуркация
    bifurk_my_1,      # Кумулятивные суммы
    SSA_my,           # SSA анализ
    specgram_my,      # Спектрограмма
)

# Пример использования
H_vvod(Y, L, K, d, m, D, R, alp, fig=figure)
Hinich_my(Y, K, d, L, R, fig=figure)
```

---

## Примеры использования

### Полный цикл анализа

```python
from functions.data_loader import DataAnalyzer
from functions.core import ChaosAnalyzer, HoelderAnalyzer
from functions import segment_my, bifurk_my, bifurk_my_1
import matplotlib.pyplot as plt

# 1. Загрузка данных
data_analyzer = DataAnalyzer()
result = data_analyzer.load_and_analyze('test.txt')
Y = data_analyzer.smoothed_data

# 2. Анализ хаотичности
chaos = ChaosAnalyzer()
chaos_result = chaos.analyze(Y, L=200, d=100, R=200)

# 3. Показатель Гёльдера
hoelder = HoelderAnalyzer()
hoelder_result = hoelder.analyze(Y, L=200, d=100, R=200)

# 4. Сегментация
J = segment_my(Y)

# 5. Бифуркация (если есть скачки)
if len(J) > 0:
    DT, H, G = bifurk_my(Y, J=J, n=1)
    bifurk_my_1(DT, H, G, L0=100, L1=100)

plt.show()
```

### Индивидуальный анализ

```python
from functions import Herst_f, fract_dim_f, Inform_f, Lyapunov_f

# Для одного окна
h = Herst_f(window)
dt = fract_dim_f(window)
i = Inform_f(window)
lyap = Lyapunov_f(window, m=30, D=4)

# Фрактальная размерность с поправкой
DT_corrected = (dt + 4 - h + 1.21 * i) / 3
```

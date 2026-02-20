# Makefile для проекта "Характеристики нелинейности и хаотичности"

# Определение операционной системы
ifeq ($(OS),Windows_NT)
    OS_NAME = windows
    BIN_EXT = .exe
    BIN_DIR = bin/windows
    PYTHON = venv\Scripts\python
    PIP = venv\Scripts\pip
    PYSIDE6_UIC = venv\Scripts\pyside6-uic
    PYINSTALLER = venv\Scripts\pyinstaller
    PYTHON_SYS = python
    MKDIR = if not exist "$1" mkdir "$1"
    RM_RF = if exist "$1" rmdir /s /q "$1"
    RM_F = if exist "$1" del /q "$1"
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Darwin)
        OS_NAME = macos
    else
        OS_NAME = linux
    endif
    BIN_EXT =
    BIN_DIR = bin/$(OS_NAME)
    PYTHON = ./venv/bin/python
    PIP = ./venv/bin/pip
    PYSIDE6_UIC = ./venv/bin/pyside6-uic
    PYINSTALLER = ./venv/bin/pyinstaller
    PYTHON_SYS = python3
    MKDIR = mkdir -p "$1"
    RM_RF = rm -rf "$1"
    RM_F = rm -f "$1"
endif

ifdef OS
    PYTHON_VENV := venv\Scripts\python.exe
    PIP_VENV := venv\Scripts\pip.exe
else
    PYTHON_VENV := venv/bin/python
    PIP_VENV := venv/bin/pip
endif

# Имя бинарного файла
BIN_NAME = vkr_analysis$(BIN_EXT)
BIN_PATH = $(BIN_DIR)/$(BIN_NAME)

.PHONY: all run install deps ui test clean help test-data refactor lint build build-clean

# Цель по умолчанию
all: install ui

# Установка зависимостей
install:
	@echo "=== Установка зависимостей ==="
	$(PYTHON_SYS) -m venv venv
	$(PYTHON_VENV) -m pip install --upgrade pip
	$(PIP_VENV) install -r requirements.txt
	@echo "=== Зависимости установлены ==="

# Проверка зависимостей
deps:
	@echo "=== Проверка зависимостей ==="
	$(PYTHON) -c "import PySide6; import numpy; import scipy; import matplotlib; print('✅ Все зависимости установлены')"

# Генерация UI файлов
ui:
	@echo "=== Генерация UI файлов ==="
	$(PYSIDE6_UIC) form.ui -o ui_form.py
	@echo "✅ UI файлы сгенерированы"

# Запуск приложения
run: deps
	@echo "=== Запуск приложения ==="
	$(PYTHON) mainwindow.py

# Рефакторинг - тестирование новой архитектуры
refactor: deps
	@echo "=== Тестирование рефакторенной версии ==="
	$(PYTHON) -c "\
from config import config, get_default_parameters; \
from utils import setup_logging, load_data_file; \
from functions import ChaosAnalyzer, HoelderAnalyzer, DataLoader; \
print('✅ Импорт всех модулей успешен'); \
params = get_default_parameters(); \
print(f'✅ Конфигурация: L={params.window_width}, d={params.window_shift}, R={params.num_windows}'); \
setup_logging(); \
print('✅ Логгирование настроено'); \
loader = DataLoader(); \
print('✅ DataLoader создан'); \
chaos = ChaosAnalyzer(); \
hoelder = HoelderAnalyzer(); \
print('✅ Анализаторы созданы'); \
print('\\n✅ Рефакторинг завершён успешно!')"

# Создание тестовых данных
test-data:
	@echo "=== Создание тестовых данных ==="
	$(call MKDIR,test_data)
	$(PYTHON) -c "\
import numpy as np; \
np.random.seed(42); \
t = np.linspace(0, 10, 1000); \
signal1 = np.sin(2 * np.pi * 5 * t) + 0.5 * np.sin(2 * np.pi * 10 * t) + np.random.randn(1000) * 0.3; \
np.savetxt('test_data/test_sinusoid.txt', signal1); \
np.random.seed(123); \
signal2 = np.cumsum(np.random.randn(5000)); \
np.savetxt('test_data/test_random_walk.txt', signal2); \
np.random.seed(456); \
signal3 = np.cumsum(np.random.randn(2000)); \
signal3[500:600] += 50; signal3[1200:1300] -= 30; \
np.savetxt('test_data/test_jumps.txt', signal3); \
np.random.seed(789); \
signal4 = np.sin(np.linspace(0, 8*np.pi, 256)) + np.random.randn(256) * 0.2; \
np.savetxt('test_data/test_short.txt', signal4); \
np.random.seed(111); \
t5 = np.linspace(0, 50, 5000); signal5 = np.zeros_like(t5); \
signal5[:1000] = np.sin(2 * np.pi * 1 * t5[:1000]); \
signal5[1000:2000] = np.sin(2 * np.pi * 5 * t5[1000:2000]); \
signal5[2000:3000] = np.sin(2 * np.pi * 10 * t5[2000:3000]); \
signal5[3000:] = np.sin(2 * np.pi * 3 * t5[3000:]); \
signal5 += np.random.randn(5000) * 0.1; \
np.savetxt('test_data/test_multifreq.txt', signal5); \
print('✅ Тестовые данные созданы в папке test_data/')"
	@echo "=== Тестовые данные созданы ==="

# Тестирование функций
test: deps
	@echo "=== Тестирование функций ==="
	$(PYTHON) -c "\
import numpy as np; \
import matplotlib; matplotlib.use('Agg'); \
from functions.Herst_f import Herst_f; \
from functions.fract_dim_f import fract_dim_f; \
from functions.Inform_f import Inform_f; \
from functions.Lyapunov_f import Lyapunov_f; \
from functions.Hoelder_f import Hoelder_f; \
from functions.Huang_f import Huang_f; \
y = np.random.randn(100); \
print(f'Herst_f: {Herst_f(y):.4f}'); \
print(f'fract_dim_f: {fract_dim_f(y):.4f}'); \
print(f'Inform_f: {Inform_f(y):.4f}'); \
print(f'Lyapunov_f: {Lyapunov_f(y, 30, 4):.4f}'); \
print(f'Hoelder_f: {Hoelder_f(y):.4f}'); \
print(f'Huang_f: {Huang_f(y):.4f}'); \
print('✅ Все функции работают')"

# Линтинг
lint: deps
	@echo "=== Проверка кода (linting) ==="
	@echo "Проверка синтаксиса Python..."
	$(PYTHON) -m py_compile config.py utils.py mainwindow.py
	$(PYTHON) -m py_compile functions/*.py widgets/*.py
	@echo "✅ Синтаксических ошибок не найдено"

# Сборка в бинарный файл
build: deps ui
	@echo "=== Сборка бинарного файла ==="
	@echo "Операционная система: $(OS_NAME)"
	@echo "Папка для бинарника: $(BIN_DIR)"
	@echo "Имя файла: $(BIN_NAME)"
	$(call MKDIR,$(BIN_DIR))
	@echo "Запуск PyInstaller..."
	$(PYINSTALLER) --clean --distpath $(BIN_DIR) --workpath build/temp build.spec
	@echo "=== Переименование файла ==="
ifeq ($(OS),Windows_NT)
	@if exist "$(BIN_DIR)\vkr_analysis\$(BIN_NAME)" ( \
		move "$(BIN_DIR)\vkr_analysis\$(BIN_NAME)" "$(BIN_PATH)" && \
		rmdir /s /q "$(BIN_DIR)\vkr_analysis" \
	)
else
	@if [ -f "$(BIN_DIR)/vkr_analysis/$(BIN_NAME)" ]; then \
		mv "$(BIN_DIR)/vkr_analysis/$(BIN_NAME)" "$(BIN_PATH)" && \
		rm -rf "$(BIN_DIR)/vkr_analysis"; \
	fi
endif
	@echo "=== Очистка временных файлов ==="
	$(call RM_RF,build/temp)
	@echo "=== Сборка завершена! ==="
	@echo "Бинарный файл: $(BIN_PATH)"

# Очистка сборки
build-clean:
	@echo "=== Очистка сборки ==="
	$(call RM_RF,bin)
	$(call RM_RF,build)
	$(call RM_RF,dist)
	$(call RM_RF,__pycache__)
	@echo "=== Сборка очищена ==="

# Очистка
clean:
	@echo "=== Очистка ==="
	$(call RM_RF,venv)
	$(call RM_RF,__pycache__)
	$(call RM_RF,functions/__pycache__)
	$(call RM_RF,widgets/__pycache__)
	$(call RM_RF,test_data)
	$(call RM_RF,bin)
	$(call RM_RF,build)
	$(call RM_RF,dist)
	$(call RM_F,ui_form.py)
	@echo "=== Очистка завершена ==="

# Помощь
help:
	@echo "Характеристики нелинейности и хаотичности"
	@echo "=========================================="
	@echo ""
	@echo "Использование:"
	@echo "  make install   - Установка зависимостей"
	@echo "  make ui        - Генерация UI файлов из form.ui"
	@echo "  make run       - Запуск приложения"
	@echo "  make test-data - Создание тестовых данных"
	@echo "  make test      - Тестирование функций"
	@echo "  make lint      - Проверка кода"
	@echo "  make build     - Сборка в бинарный файл (авто-ОС)"
	@echo "  make build-clean - Очистка сборки"
	@echo "  make clean     - Очистка временных файлов"
	@echo "  make deps      - Проверка зависимостей"
	@echo "  make help      - Показать эту справку"
	@echo ""
	@echo "Быстрый запуск:"
	@echo "  make install ui test-data run"
	@echo ""
	@echo "Сборка релиза:"
	@echo "  make install build"
	@echo ""
	@echo "Определение ОС:"
	@echo "  make info"

# Информация о системе
info:
	@echo "=== Информация о системе ==="
	@echo "Операционная система: $(OS_NAME)"
	@echo "Папка для бинарника: $(BIN_DIR)"
	@echo "Имя бинарного файла: $(BIN_NAME)"
	@echo "Полный путь: $(BIN_PATH)"

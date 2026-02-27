# Руководство по сборке

## 📦 Сборка бинарного файла

Проект может быть собран в автономный бинарный файл с помощью PyInstaller.

### Автоматическое определение ОС

Makefile автоматически определяет операционную систему и создаёт бинарный файл в соответствующей папке:

| ОС | Папка | Имя файла |
|----|-------|-----------|
| Linux | `bin/linux/` | `vkr_analysis` |
| macOS | `bin/macos/` | `vkr_analysis` |
| Windows | `bin/windows/` | `vkr_analysis.exe` |

### Быстрая сборка

```bash
# Установка зависимостей и сборка
make install build
```

### Пошаговая сборка

```bash
# 1. Установка зависимостей
make install

# 2. Генерация UI
make ui

# 3. Сборка
make build
```

### Проверка системы

```bash
# Информация об ОС и пути к бинарнику
make info
```

## 📁 Структура после сборки

```
vkr/
├── bin/
│   ├── linux/
│   │   └── vkr_analysis      # Linux бинарник
│   ├── macos/
│   │   └── vkr_analysis      # macOS бинарник
│   └── windows/
│       └── vkr_analysis.exe  # Windows бинарник
├── build/                     # Временные файлы сборки
├── build.spec                 # Spec-файл PyInstaller
└── ...
```

## 🔧 Настройки сборки

### Spec-файл (build.spec)

Основные настройки в `build.spec`:

```python
# Имя исполняемого файла
name='vkr_analysis'

# Консольное приложение (False = GUI)
console=False

# Сжатие (UPX)
upx=True

# Включаемые файлы
datas=[
    ('form.ui', '.'),
]
```

### Скрытые импорты

В spec-файле указаны все необходимые скрытые импорты:

```python
hiddenimports=[
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'matplotlib.backends.backend_qtagg',
    'scipy.io.matlab',
    'scipy.signal',
    'scipy.stats',
    'numpy',
]
```

## 🧹 Очистка

```bash
# Очистка результатов сборки
make build-clean

# Полная очистка (включая venv)
make clean
```

## 🐛 Устранение проблем

### Ошибка: "PyInstaller not found"

```bash
make install
# или
pip install pyinstaller
```

### Ошибка: "form.ui not found"

```bash
# Убедитесь, что вы в корневой директории проекта
ls form.ui
```

### Бинарник не запускается

Проверьте зависимости системы:

**Linux:**
```bash
# Для PySide6
sudo apt-get install libxcb-xinerama0 libxcb-cursor0
```

**macOS:**
```bash
# Разрешение в System Preferences → Security & Privacy
```

**Windows:**
```bash
# Установите Visual C++ Redistributable
```

### Большой размер бинарника

Это нормально для Python приложений. Размер ~50-100 МБ включает:
- Python интерпретатор
- PySide6 (Qt)
- NumPy, SciPy, Matplotlib

## 📊 Сравнение размеров

| Компонент | Размер (примерно) |
|-----------|-------------------|
| Исходный код | ~500 КБ |
| С зависимостями | ~300 МБ (venv) |
| Бинарный файл | ~80-120 МБ |

## 🚀 Распространение

### Linux

```bash
# Копирование бинарника
cp bin/linux/vkr_analysis /usr/local/bin/
chmod +x /usr/local/bin/vkr_analysis

# Запуск
vkr_analysis
```

### macOS

```bash
# Копирование в Applications
cp -r bin/macos/vkr_analysis /Applications/

# Или создание DMG
create-dmg bin/macos/vkr_analysis
```

### Windows

```bash
# Копирование
copy bin\windows\vkr_analysis.exe C:\Program Files\VKR\

# Создание ярлыка
```

## 📝 Примечания

**Сборка на той же ОС**: Бинарник работает только на той же ОС, на которой собран

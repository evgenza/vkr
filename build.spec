# -*- mode: python ; coding: utf-8 -*-
"""
Spec-файл для PyInstaller
Сборка приложения "Характеристики нелинейности и хаотичности"

Использование:
    pyinstaller build.spec

Бинарный файл будет создан в папке bin/<os>/
"""

import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Определение ОС для правильного пути
import platform
if platform.system() == 'Linux':
    OS_DIR = 'linux'
elif platform.system() == 'Darwin':
    OS_DIR = 'macos'
else:
    OS_DIR = 'windows'

block_cipher = None

# Скрытые импорты для всех модулей
hiddenimports = (
    # PySide6
    collect_submodules('PySide6.QtCore') +
    collect_submodules('PySide6.QtGui') +
    collect_submodules('PySide6.QtWidgets') +
    
    # Matplotlib
    collect_submodules('matplotlib') +
    ['matplotlib.backends.backend_qtagg'] +
    
    # SciPy
    collect_submodules('scipy.io') +
    collect_submodules('scipy.io.matlab') +
    collect_submodules('scipy.signal') +
    collect_submodules('scipy.stats') +
    collect_submodules('scipy.fft') +
    
    # NumPy
    collect_submodules('numpy') +
    
    # Модули проекта
    ['functions.H_vvod', 'functions.Hinich_my', 'functions.Herst_my',
     'functions.Hoelder_my', 'functions.segment_my', 'functions.Curth_my',
     'functions.bifurk_my', 'functions.bifurk_my_1', 'functions.SSA_my',
     'functions.specgram_my',
     'functions.Herst_f', 'functions.Lyapunov_f', 'functions.fract_dim_f',
     'functions.Inform_f', 'functions.Hoelder_f', 'functions.Huang_f',
     'functions.GLSTAT', 'functions.exp_smooth_twice',
     'functions.base',
     'widgets.matplotlib_widget',
     'ui_form', 'config', 'utils']
)

# Сбор данных
datas = (
    collect_data_files('matplotlib') +
    collect_data_files('scipy.io') +
    [('form.ui', '.'), ('requirements.txt', '.'), ('icons/icon_512x512.png', 'icons')]
)

binaries = []

a = Analysis(
    ['mainwindow.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'jupyter',
        'IPython',
        'notebook',
        'qtconsole',
        'spyder',
        'pylab',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='vkr_analysis',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False для GUI приложения
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icons/icon_512x512.png',  # Иконка приложения
)

# Копирование в правильную папку
import shutil
import os

def post_build():
    """Функция для копирования бинарника в правильную папку"""
    dist_dir = f'bin/{OS_DIR}'
    if os.path.exists('dist/vkr_analysis'):
        os.makedirs(dist_dir, exist_ok=True)
        if os.path.isfile('dist/vkr_analysis'):
            shutil.move('dist/vkr_analysis', f'{dist_dir}/vkr_analysis')
        elif os.path.isdir('dist/vkr_analysis'):
            shutil.move('dist/vkr_analysis', f'{dist_dir}/vkr_analysis')

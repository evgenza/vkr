"""
Главное окно приложения
"""
import sys
import logging
import os
from typing import Optional, List, Dict, Any, Callable

import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox,
    QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QFrame,
)
from PySide6.QtGui import QIcon, QCursor, QIntValidator, QDoubleValidator
from PySide6.QtCore import Qt

from ui_form import Ui_MainWindow
from widgets.matplotlib_widget import PlotDialog

from config import config
from utils import setup_logging, load_data_file, get_signal_properties

from functions import (
    H_vvod, Hinich_my, Herst_my, Hoelder_my,
    segment_my, Curth_my, bifurk_my, bifurk_my_1,
    SSA_my, specgram_my
)
from functions.feature_extractor import extract_features, FEATURE_NAMES
from functions.anomaly_model import AnomalyModel

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._set_app_icon()

        self.Y: Optional[np.ndarray] = None
        self.J: Optional[np.ndarray] = None
        self.DT: Optional[np.ndarray] = None
        self.H: Optional[np.ndarray] = None
        self.G: Optional[np.ndarray] = None

        self._plot_dialogs: List[PlotDialog] = []
        self._anomaly_model: Optional[AnomalyModel] = None
        self._training_features: Optional[np.ndarray] = None
        self._training_file_names: List[str] = []

        self._setup_validators()
        self._connect_signals()
        self._connect_menu_actions()
        self._setup_diagnostic_panel()
        self._load_default_parameters()

        logger.info("MainWindow инициализировано")

    def _set_app_icon(self):
        """Установка иконки приложения"""
        icon_paths = [
            'icons/icon_512x512.png',
            'icons/icon_256x256.png',
            'icons/icon_128x128.png'
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                logger.info(f"✅ Иконка установлена: {icon_path}")
                return
        
        logger.warning("⚠️  Иконка не найдена")

    def _setup_validators(self):
        """Установка валидаторов для полей ввода"""
        rules = config.validation
        self.ui.lineEdit_L.setValidator(
            QIntValidator(rules.window_width[0], rules.window_width[1]))
        self.ui.lineEdit_K.setValidator(
            QIntValidator(rules.start_offset[0], rules.start_offset[1]))
        self.ui.lineEdit_d.setValidator(
            QIntValidator(rules.window_shift[0], rules.window_shift[1]))
        self.ui.lineEdit_m.setValidator(
            QIntValidator(rules.num_bands[0], rules.num_bands[1]))
        self.ui.lineEdit_D.setValidator(
            QDoubleValidator(rules.deviation[0], rules.deviation[1], 1))
        self.ui.lineEdit_R.setValidator(
            QIntValidator(rules.num_windows[0], rules.num_windows[1]))
        self.ui.lineEdit_alp.setValidator(
            QDoubleValidator(rules.smoothing_alpha[0], rules.smoothing_alpha[1], 4))
        self.ui.lineEdit_n.setValidator(
            QIntValidator(rules.jump_number[0], rules.jump_number[1]))

    def _connect_signals(self):
        """Подключение сигналов"""
        connections = {
            self.ui.pushButton_exit: self.close,
            self.ui.pushButton_inputData: self.on_input_data,
            self.ui.pushButton_hinich: self.on_hinich,
            self.ui.pushButton_herstLyapunov: self.on_herst_lyapunov,
            self.ui.pushButton_hoelder: self.on_hoelder,
            self.ui.pushButton_segmentation: self.on_segmentation,
            self.ui.pushButton_curth: self.on_curth,
            self.ui.pushButton_bifurcation: self.on_bifurcation,
            self.ui.pushButton_cumulative: self.on_cumulative,
            self.ui.pushButton_oscillations: self.on_oscillations,
            self.ui.pushButton_spectrogram: self.on_spectrogram,
        }

        for button, handler in connections.items():
            button.clicked.connect(handler)

    def _connect_menu_actions(self):
        self.ui.actionOpen.triggered.connect(self.on_input_data)
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionAbout.triggered.connect(self.on_about)

    def on_about(self):
        QMessageBox.about(
            self,
            "О программе",
            f"<h3>{config.title}</h3>"
            f"<p>{config.subtitle}</p>"
            "<p>Версия 2.0</p>"
            "<p>Приложение для анализа временных рядов "
            "методами нелинейной динамики.</p>")

    def _load_default_parameters(self):
        """Загрузка параметров по умолчанию"""
        params = config.parameters
        self.ui.lineEdit_L.setText(str(params.window_width))
        self.ui.lineEdit_K.setText(str(params.start_offset))
        self.ui.lineEdit_d.setText(str(params.window_shift))
        self.ui.lineEdit_m.setText(str(params.num_bands))
        self.ui.lineEdit_D.setText(str(params.deviation))
        self.ui.lineEdit_R.setText(str(params.num_windows))
        self.ui.lineEdit_alp.setText(str(params.smoothing_alpha))
        self.ui.lineEdit_n.setText(str(params.jump_number))

    def _create_plot_dialog(self, title: str,
                            figsize: tuple = (12, 8)) -> PlotDialog:
        dialog = PlotDialog(self, title=title, figsize=figsize)
        dialog.finished.connect(lambda: self._on_dialog_closed(dialog))
        self._plot_dialogs.append(dialog)
        return dialog

    def _on_dialog_closed(self, dialog: PlotDialog):
        if dialog in self._plot_dialogs:
            self._plot_dialogs.remove(dialog)

    def _show_warning(self, title: str, message: str):
        QMessageBox.warning(self, title, message)
        logger.warning("%s: %s", title, message)

    def _show_error(self, title: str, error: Exception, context: str = ""):
        message = f"{context}: {error}" if context else str(error)
        QMessageBox.critical(self, title, message)
        logger.error("%s: %s", title, message, exc_info=True)

    def _run_analysis(self, title: str, figsize: tuple,
                      func: Callable, param_keys: List[str],
                      **extra_kwargs) -> Optional[Any]:
        """
        Общий шаблон запуска анализа: проверка данных, параметры, курсор ожидания, вызов.
        """
        if not self._check_data_loaded():
            return None
        params = self.get_parameters()
        if params is None:
            return None
        if not self._validate_window_params(params):
            return None

        try:
            QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
            dialog = self._create_plot_dialog(title, figsize)
            kwargs = {key: params[key] for key in param_keys}
            kwargs.update(extra_kwargs)
            kwargs['fig'] = dialog.figure
            result = func(self.Y, **kwargs)
            dialog.show_plot()
            return result
        except Exception as e:
            self._show_error("Ошибка анализа", e, title)
            return None
        finally:
            QApplication.restoreOverrideCursor()

    def _validate_window_params(self, params: Dict[str, Any]) -> bool:
        """Проверка совместимости параметров окна с длиной данных."""
        if self.Y is None:
            return False
        data_len = len(self.Y)
        window_width = params.get('window_width', 0)
        start_offset = params.get('start_offset', 0)
        window_shift = params.get('window_shift', 1)
        num_windows = params.get('num_windows', 1)
        required_len = start_offset + window_width + (num_windows - 1) * window_shift
        if window_width > data_len:
            self._show_warning(
                "Ошибка параметров",
                f"Ширина окна L={window_width} превышает длину данных ({data_len}).\n"
                f"Уменьшите L или загрузите больше данных.")
            return False
        if required_len > data_len:
            max_windows = max(1, (data_len - start_offset - window_width) // window_shift + 1)
            self._show_warning(
                "Ошибка параметров",
                f"Параметры требуют {required_len} отсчётов, доступно {data_len}.\n"
                f"Максимальное число окон при текущих параметрах: {max_windows}.")
            return False
        return True

    def get_parameters(self) -> Optional[Dict[str, Any]]:
        try:
            window_width = int(self.ui.lineEdit_L.text())
            start_offset = int(self.ui.lineEdit_K.text())
            window_shift = int(self.ui.lineEdit_d.text())
            num_bands = int(self.ui.lineEdit_m.text())
            deviation = float(self.ui.lineEdit_D.text())
            num_windows = int(self.ui.lineEdit_R.text())
            smoothing_alpha = float(self.ui.lineEdit_alp.text())
            jump_number = int(self.ui.lineEdit_n.text())

            rules = config.validation
            errors = []

            if window_width < rules.window_width[0] or window_width > rules.window_width[1]:
                errors.append(f"Ширина окна: [{rules.window_width[0]}, {rules.window_width[1]}]")
            if start_offset < rules.start_offset[0]:
                errors.append("Начало отсчёта не может быть отрицательным")
            if window_shift < rules.window_shift[0]:
                errors.append("Сдвиг окна должен быть положительным")
            if num_bands < rules.num_bands[0]:
                errors.append("Число полос должно быть положительным")
            if num_windows < rules.num_windows[0]:
                errors.append("Число окон должно быть положительным")
            if not (rules.smoothing_alpha[0] <= smoothing_alpha <= rules.smoothing_alpha[1]):
                errors.append(f"Альфа: [{rules.smoothing_alpha[0]}, {rules.smoothing_alpha[1]}]")
            if jump_number < rules.jump_number[0]:
                errors.append(f"Номер скачка >= {rules.jump_number[0]}")

            if errors:
                raise ValueError("; ".join(errors))

            return {
                'window_width': window_width,
                'start_offset': start_offset,
                'window_shift': window_shift,
                'num_bands': num_bands,
                'deviation': deviation,
                'num_windows': num_windows,
                'smoothing_alpha': smoothing_alpha,
                'jump_number': jump_number,
            }

        except ValueError as e:
            self._show_warning("Ошибка ввода параметров", str(e))
            return None

    def on_input_data(self):
        params = self.get_parameters()
        if params is None:
            return

        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Выберите файл данных", "", config.files.FILTER)
            if not file_path:
                return

            QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
            logger.info("Загрузка файла: %s", file_path)
            self.Y = load_data_file(file_path)

            if self.Y is None:
                raise ValueError("Не удалось загрузить данные")

            dialog = self._create_plot_dialog(
                "Временной ряд данных", figsize=config.plots.figsize_main)
            result = H_vvod(self.Y, fig=dialog.figure, **{
                k: params[k] for k in (
                    'window_width', 'start_offset', 'window_shift',
                    'num_bands', 'deviation', 'num_windows', 'smoothing_alpha')
            })
            dialog.set_data({'Y': self.Y, 'Y_сглаженный': result})
            dialog.show_plot()

            props = get_signal_properties(self.Y)
            basename = os.path.basename(file_path)
            self.ui.fileComboBox.addItem(basename)
            self.ui.fileComboBox.setCurrentIndex(
                self.ui.fileComboBox.count() - 1)
            self.ui.statusbar.showMessage(
                f"Файл: {basename} | {props['length']} отсчётов | "
                f"min={props['min']:.2f}, max={props['max']:.2f}")
            logger.info("Данные загружены: %d отсчётов, min=%.2f, max=%.2f",
                        props['length'], props['min'], props['max'])

        except Exception as e:
            self._show_error("Ошибка загрузки данных", e)
        finally:
            QApplication.restoreOverrideCursor()

    def _check_data_loaded(self) -> bool:
        if self.Y is None:
            self._show_warning("Предупреждение", "Сначала загрузите данные!")
            return False
        return True

    _WINDOW_PARAMS = ['start_offset', 'window_shift', 'window_width', 'num_windows']

    def on_hinich(self):
        self._run_analysis("Тест Хинича", config.plots.figsize_main,
                           Hinich_my, self._WINDOW_PARAMS)

    def on_herst_lyapunov(self):
        self._run_analysis(
            "Показатели Херста и Ляпунова", config.plots.figsize_wide,
            Herst_my, self._WINDOW_PARAMS + ['num_bands', 'deviation'])

    def on_hoelder(self):
        self._run_analysis(
            "Показатель Гёльдера", config.plots.figsize_main,
            Hoelder_my,
            self._WINDOW_PARAMS + ['num_bands', 'deviation'])

    def on_segmentation(self):
        result = self._run_analysis(
            "Сегментация - скачки скорости", config.plots.figsize_main,
            segment_my, self._WINDOW_PARAMS)
        if result is not None:
            self.J = result
            self._plot_dialogs[-1].set_data({'J_скачки': result})

    def on_curth(self):
        self._run_analysis("Куртозис и пик-фактор", config.plots.figsize_main,
                           Curth_my, self._WINDOW_PARAMS)

    def on_bifurcation(self):
        if not self._check_data_loaded():
            return
        if self.J is None or len(self.J) == 0:
            self._show_warning("Предупреждение", "Сначала выполните сегментацию!")
            return

        params = self.get_parameters()
        if params is None:
            return
        if not self._validate_window_params(params):
            return

        try:
            QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
            dialog = self._create_plot_dialog(
                f"Бифуркация #{params['jump_number']}", config.plots.figsize_wide)
            self.DT, self.H, self.G = bifurk_my(
                self.Y, num_bands=params['num_bands'],
                deviation=params['deviation'],
                L0=config.parameters.L0, L1=config.parameters.L1,
                J=self.J, jump_number=params['jump_number'],
                fig=dialog.figure)
            dialog.set_data({'DT': self.DT, 'H_Херст': self.H, 'G_Гёльдер': self.G})
            dialog.show_plot()
        except Exception as e:
            self._show_error("Ошибка анализа", e, "Бифуркация")
        finally:
            QApplication.restoreOverrideCursor()

    def on_cumulative(self):
        if self.DT is None or self.H is None or self.G is None:
            self._show_warning("Предупреждение",
                               "Сначала выполните анализ бифуркации!")
            return

        try:
            QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
            dialog = self._create_plot_dialog(
                "Кумулятивные суммы", config.plots.figsize_large)
            bifurk_my_1(self.DT, self.H, self.G,
                        L0=config.parameters.L0, L1=config.parameters.L1,
                        fig=dialog.figure)
            dialog.set_data({'DT': self.DT, 'H_Херст': self.H, 'G_Гёльдер': self.G})
            dialog.show_plot()
        except Exception as e:
            self._show_error("Ошибка анализа", e, "Кумулятивные суммы")
        finally:
            QApplication.restoreOverrideCursor()

    def on_oscillations(self):
        self._run_analysis("SSA анализ - колебания", config.plots.figsize_main,
                           SSA_my, self._WINDOW_PARAMS)

    def on_spectrogram(self):
        if not self._check_data_loaded():
            return
        try:
            QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
            dialog = self._create_plot_dialog(
                "Спектрограмма сигнала", config.plots.figsize_wide)
            S, F, T = specgram_my(self.Y, fig=dialog.figure)
            dialog.set_data({'S_спектр': S, 'F_частоты': F, 'T_время': T})
            dialog.show_plot()
        except Exception as e:
            self._show_error("Ошибка анализа", e, "Спектрограмма")
        finally:
            QApplication.restoreOverrideCursor()

    # ── Панель диагностики ─────────────────────────────────────────────

    def _setup_diagnostic_panel(self):
        """Панель диагностики подшипников — справа от параметров скачка."""
        group = QGroupBox("Диагностика подшипников")
        group.setMinimumWidth(210)
        group.setStyleSheet(
            "QGroupBox { font-weight: bold; border: 2px solid #e74c3c; "
            "border-radius: 8px; margin-top: 10px; padding-top: 18px; } "
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; "
            "padding: 0 5px; color: #e74c3c; }"
        )

        # Стиль кнопок панели (по умолчанию белый текст без фона)
        _btn_style = (
            "QPushButton {{ background: qlineargradient("
            "x1:0,y1:0,x2:0,y2:1, stop:0 {c1}, stop:1 {c2}); }}"
            "QPushButton:hover {{ background: qlineargradient("
            "x1:0,y1:0,x2:0,y2:1, stop:0 {c1h}, stop:1 {c1}); }}"
            "QPushButton:pressed {{ background: qlineargradient("
            "x1:0,y1:0,x2:0,y2:1, stop:0 {c2}, stop:1 {c2p}); }}"
        )

        # ── Алгоритм ──
        self._diag_combo = QComboBox()
        self._diag_combo.addItem("Быстрая диагностика")
        self._diag_combo.addItem("Точная диагностика")
        self._diag_combo.setItemData(
            0, "Isolation Forest — быстрый алгоритм,\n"
            "хорошо работает на больших объёмах данных", Qt.ToolTipRole)
        self._diag_combo.setItemData(
            1, "One-Class SVM — точнее определяет границу нормы,\n"
            "лучше для малых выборок", Qt.ToolTipRole)

        # ── Загрузка данных + Обучение ──
        btn_load_data = QPushButton("Загрузить данные")
        btn_load_data.setToolTip("Загрузить файлы здоровых подшипников для обучения")
        btn_load_data.setMinimumHeight(35)
        btn_load_data.setStyleSheet(_btn_style.format(
            c1='#3498db', c2='#2980b9', c1h='#5dade2', c2p='#1f618d'))
        btn_load_data.clicked.connect(self.on_load_training_data)

        btn_train = QPushButton("Обучить")
        btn_train.setToolTip("Обучить модель на загруженных данных")
        btn_train.setMinimumHeight(35)
        btn_train.setStyleSheet(_btn_style.format(
            c1='#27ae60', c2='#229954', c1h='#58d68d', c2p='#1e8449'))
        btn_train.clicked.connect(self.on_train_model)

        # ── Разделитель ──
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet("color: #bdc3c7;")

        # ── Диагностика ──
        btn_diagnose = QPushButton("Диагностика")
        btn_diagnose.setToolTip("Проверить текущий сигнал на аномалии")
        btn_diagnose.setMinimumHeight(35)
        btn_diagnose.setStyleSheet(_btn_style.format(
            c1='#e74c3c', c2='#c0392b', c1h='#ec7063', c2p='#922b21'))
        btn_diagnose.clicked.connect(self.on_diagnose)

        # ── Разделитель ──
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("color: #bdc3c7;")

        # ── Сохранить / Загрузить модель ──
        btn_save = QPushButton("Сохранить")
        btn_save.setToolTip("Сохранить обученную модель в файл")
        btn_save.setMinimumHeight(30)
        btn_save.setStyleSheet(_btn_style.format(
            c1='#95a5a6', c2='#7f8c8d', c1h='#b2babb', c2p='#566573'))
        btn_save.clicked.connect(self.on_save_model)

        btn_load_model = QPushButton("Загрузить")
        btn_load_model.setToolTip("Загрузить ранее сохранённую модель")
        btn_load_model.setMinimumHeight(30)
        btn_load_model.setStyleSheet(_btn_style.format(
            c1='#95a5a6', c2='#7f8c8d', c1h='#b2babb', c2p='#566573'))
        btn_load_model.clicked.connect(self.on_load_model)

        # ── Статус ──
        self._diag_status = QLabel("Модель не обучена")
        self._diag_status.setWordWrap(True)
        self._diag_status.setStyleSheet(
            "font-weight: normal; font-size: 9pt; color: #7f8c8d;")

        # ── Компоновка ──
        vbox = QVBoxLayout(group)
        vbox.setSpacing(6)
        vbox.addWidget(self._diag_combo)
        vbox.addWidget(btn_load_data)
        vbox.addWidget(btn_train)
        vbox.addWidget(sep1)
        vbox.addWidget(btn_diagnose)
        vbox.addWidget(sep2)

        row_model = QHBoxLayout()
        row_model.addWidget(btn_save)
        row_model.addWidget(btn_load_model)
        vbox.addLayout(row_model)

        vbox.addWidget(self._diag_status)
        vbox.addStretch()

        # Вставляем в ряд параметров (после "Параметры скачка")
        self.ui.horizontalLayout_main.addWidget(group, 1)

    def on_load_training_data(self):
        """Загрузить файлы здоровых подшипников для обучения."""
        params = self.get_parameters()
        if params is None:
            return

        files, _ = QFileDialog.getOpenFileNames(
            self, "Выберите файлы здоровых подшипников", "",
            config.files.FILTER)
        if not files:
            return

        try:
            QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))

            all_features = []
            loaded_names = []
            for fp in files:
                Y = load_data_file(fp)
                if Y is None:
                    logger.warning("Пропуск файла (not loaded): %s", fp)
                    continue
                X = extract_features(
                    Y,
                    start_offset=params['start_offset'],
                    window_shift=params['window_shift'],
                    window_width=params['window_width'],
                    num_windows=params['num_windows'],
                    num_bands=params['num_bands'],
                    deviation=params['deviation'],
                )
                if X.shape[0] > 0:
                    all_features.append(X)
                    loaded_names.append(os.path.basename(fp))

            if not all_features:
                self._show_warning("Ошибка", "Не удалось извлечь признаки ни из одного файла.")
                return

            self._training_features = np.vstack(all_features)
            self._training_file_names = loaded_names

            n_files = len(loaded_names)
            n_windows = self._training_features.shape[0]
            self._diag_status.setText(
                f"Загружено: {n_files} файл(ов), {n_windows} окон")
            QMessageBox.information(
                self, "Данные загружены",
                f"Загружено {n_files} файл(ов).\n"
                f"Извлечено {n_windows} окон признаков.\n"
                f"Теперь нажмите \u00abОбучить\u00bb.")

        except Exception as e:
            self._show_error("Ошибка загрузки данных", e)
        finally:
            QApplication.restoreOverrideCursor()

    def on_train_model(self):
        """Обучить модель на загруженных данных."""
        if self._training_features is None:
            self._show_warning("Предупреждение",
                              "Сначала загрузите данные здоровых подшипников!")
            return

        try:
            QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))

            alg = 'ocsvm' if self._diag_combo.currentIndex() == 1 else 'iforest'
            self._anomaly_model = AnomalyModel(algorithm=alg)
            self._anomaly_model.train(
                self._training_features,
                file_names=self._training_file_names)

            self._diag_status.setText(self._anomaly_model.info)
            QMessageBox.information(
                self, "Обучение завершено",
                f"Модель обучена успешно.\n{self._anomaly_model.info}")

        except Exception as e:
            self._show_error("Ошибка обучения", e)
        finally:
            QApplication.restoreOverrideCursor()

    def on_diagnose(self):
        """Диагностировать текущий загруженный сигнал."""
        if not self._check_data_loaded():
            return
        if self._anomaly_model is None or not self._anomaly_model.is_trained:
            self._show_warning("Предупреждение",
                               "Сначала обучите или загрузите модель!")
            return

        params = self.get_parameters()
        if params is None:
            return
        if not self._validate_window_params(params):
            return

        try:
            QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
            X = extract_features(
                self.Y,
                start_offset=params['start_offset'],
                window_shift=params['window_shift'],
                window_width=params['window_width'],
                num_windows=params['num_windows'],
                num_bands=params['num_bands'],
                deviation=params['deviation'],
            )

            result = self._anomaly_model.predict(X)

            # График диагностики
            dialog = self._create_plot_dialog(
                "Диагностика подшипника", figsize=(14, 8))
            fig = dialog.figure
            ax1, ax2 = fig.subplots(2, 1)

            windows = np.arange(X.shape[0])
            colors = ['green' if l == 1 else 'red' for l in result.labels]

            ax1.bar(windows, result.scores, color=colors, width=1.0)
            ax1.axhline(y=0, color='black', linewidth=1, linestyle='--')
            ax1.set_title(f'Результат: {result.verdict}  |  '
                          f'Аномалий: {result.anomaly_count}/{result.total_windows} '
                          f'({result.anomaly_pct:.1f}%)',
                          fontsize=13, fontweight='bold')
            ax1.set_ylabel('Скор аномалии')
            ax1.set_xlabel('Номер окна')
            ax1.grid(True, alpha=0.3)

            # Временной ряд с подсветкой аномальных участков
            ax2.plot(self.Y, 'b', linewidth=0.5, alpha=0.7)
            for idx in result.anomaly_indices:
                start = params['start_offset'] + idx * params['window_shift']
                end = min(start + params['window_width'], len(self.Y))
                ax2.axvspan(start, end, color='red', alpha=0.3)
            ax2.set_title('Сигнал с подсветкой аномальных участков',
                          fontsize=13, fontweight='bold')
            ax2.set_ylabel('Амплитуда')
            ax2.set_xlabel('Отсчёт')
            ax2.grid(True, alpha=0.3)

            # Данные для экспорта
            export_data = {name: X[:, i] for i, name in enumerate(FEATURE_NAMES)}
            export_data['Результат'] = result.labels
            export_data['Скор'] = result.scores
            dialog.set_data(export_data)
            dialog.show_plot()

            self._diag_status.setText(result.verdict)

        except Exception as e:
            self._show_error("Ошибка диагностики", e)
        finally:
            QApplication.restoreOverrideCursor()

    def on_save_model(self):
        """Сохранить обученную модель."""
        if self._anomaly_model is None or not self._anomaly_model.is_trained:
            self._show_warning("Предупреждение", "Модель не обучена.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить модель", "model.pkl",
            "Модель (*.pkl);;Все файлы (*)")
        if path:
            try:
                self._anomaly_model.save(path)
                QMessageBox.information(self, "Сохранено",
                                        f"Модель сохранена: {path}")
            except Exception as e:
                self._show_error("Ошибка сохранения", e)

    def on_load_model(self):
        """Загрузить ранее сохранённую модель."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Загрузить модель", "",
            "Модель (*.pkl);;Все файлы (*)")
        if path:
            try:
                self._anomaly_model = AnomalyModel.load(path)
                self._diag_status.setText(self._anomaly_model.info)
                QMessageBox.information(self, "Загружено",
                                        f"Модель загружена.\n{self._anomaly_model.info}")
            except Exception as e:
                self._show_error("Ошибка загрузки", e)


if __name__ == "__main__":
    setup_logging()
    logger.info("Запуск приложения")

    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()

    sys.exit(app.exec())

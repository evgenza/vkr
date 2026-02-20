"""
Главное окно приложения
"""
import sys
import logging
import os
from typing import Optional, List, Dict, Any, Callable

import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
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

        self._setup_validators()
        self._connect_signals()
        self._connect_menu_actions()
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
            H_vvod(self.Y, fig=dialog.figure, **{
                k: params[k] for k in (
                    'window_width', 'start_offset', 'window_shift',
                    'num_bands', 'deviation', 'num_windows', 'smoothing_alpha')
            })
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
            specgram_my(self.Y, fig=dialog.figure)
            dialog.show_plot()
        except Exception as e:
            self._show_error("Ошибка анализа", e, "Спектрограмма")
        finally:
            QApplication.restoreOverrideCursor()


if __name__ == "__main__":
    # Настройка логгирования
    setup_logging()
    logger.info("Запуск приложения")

    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()

    sys.exit(app.exec())

"""
Виджет matplotlib для интеграции графиков в Qt
"""
import csv
import logging
from typing import Optional, Dict, Any

import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDialog, QSizePolicy,
    QPushButton, QFileDialog, QMessageBox,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


class MatplotlibWidget(QWidget):
    """Виджет для встраивания matplotlib графиков в Qt"""
    
    def __init__(self, parent=None, figsize=(10, 6)):
        super().__init__(parent)
        
        # Создание Figure
        self.figure = Figure(figsize=figsize, dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Панель инструментов matplotlib
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
    
    def clear(self):
        """Очистить фигуру"""
        self.figure.clear()
        self.canvas.draw()
    
    def draw(self):
        """Обновить canvas"""
        self.figure.tight_layout()
        self.canvas.draw()


class PlotDialog(QDialog):
    """Диалоговое окно для отображения графиков matplotlib"""

    # Фильтр для экспорта графиков
    _PLOT_FILTER = (
        "PNG (*.png);;"
        "PDF (*.pdf);;"
        "SVG (*.svg);;"
        "Все файлы (*)"
    )

    # Фильтр для экспорта данных
    _DATA_FILTER = (
        "Excel (*.xlsx);;"
        "CSV (*.csv);;"
        "Все файлы (*)"
    )

    def __init__(self, parent=None, title="График", figsize=(12, 8),
                 data: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(int(figsize[0] * 100), int(figsize[1] * 100))
        self._title = title
        self._data = data

        # Виджет matplotlib
        self.plot_widget = MatplotlibWidget(self, figsize=figsize)

        # Кнопки экспорта
        btn_save_plot = QPushButton("Сохранить график")
        btn_save_plot.clicked.connect(self._on_save_plot)

        btn_export_data = QPushButton("Экспорт данных")
        btn_export_data.clicked.connect(self._on_export_data)
        btn_export_data.setEnabled(data is not None)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save_plot)
        btn_layout.addWidget(btn_export_data)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.plot_widget)
        layout.addLayout(btn_layout)

        self._btn_export_data = btn_export_data

    def set_data(self, data: Dict[str, Any]):
        """Установить данные для экспорта (можно после создания диалога)."""
        self._data = data
        self._btn_export_data.setEnabled(True)

    @property
    def figure(self):
        """Доступ к фигуре matplotlib"""
        return self.plot_widget.figure

    def draw(self):
        """Обновить график"""
        self.plot_widget.draw()

    def show_plot(self):
        """Показать диалог с графиком"""
        self.draw()
        self.show()

    # -- экспорт графика ------------------------------------------------

    def _on_save_plot(self):
        """Сохранить текущий график в файл (PNG/PDF/SVG)."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить график", self._title, self._PLOT_FILTER)
        if not path:
            return
        try:
            self.figure.savefig(path, dpi=150, bbox_inches='tight')
            logger.info("График сохранён: %s", path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить график:\n{e}")
            logger.error("Ошибка сохранения графика: %s", e, exc_info=True)

    # -- экспорт данных --------------------------------------------------

    def _on_export_data(self):
        """Экспортировать данные анализа в CSV или Excel."""
        if self._data is None:
            QMessageBox.warning(self, "Предупреждение",
                                "Нет данных для экспорта.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт данных", self._title, self._DATA_FILTER)
        if not path:
            return

        try:
            if path.lower().endswith('.xlsx'):
                self._write_xlsx(path, self._data)
            else:
                self._write_csv(path, self._data)
            logger.info("Данные экспортированы: %s", path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось экспортировать данные:\n{e}")
            logger.error("Ошибка экспорта данных: %s", e, exc_info=True)

    @staticmethod
    def _write_csv(path: str, data: Dict[str, Any]):
        """Записать словарь данных в CSV-файл.

        Поддерживает скаляры, списки и np.ndarray.
        Столбцы выравниваются по длине самого длинного массива.
        """
        columns: Dict[str, list] = {}
        for key, val in data.items():
            if isinstance(val, np.ndarray):
                columns[key] = val.tolist()
            elif isinstance(val, (list, tuple)):
                columns[key] = list(val)
            else:
                columns[key] = [val]

        max_len = max((len(v) for v in columns.values()), default=0)
        headers = list(columns.keys())

        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(headers)
            for i in range(max_len):
                row = [
                    cols[i] if i < len(cols) else ''
                    for cols in columns.values()
                ]
                writer.writerow(row)

    @staticmethod
    def _write_xlsx(path: str, data: Dict[str, Any]):
        """Записать словарь данных в Excel-файл (.xlsx)."""
        from openpyxl import Workbook

        columns: Dict[str, list] = {}
        for key, val in data.items():
            if isinstance(val, np.ndarray):
                columns[key] = val.tolist()
            elif isinstance(val, (list, tuple)):
                columns[key] = list(val)
            else:
                columns[key] = [val]

        wb = Workbook()
        ws = wb.active
        ws.title = "Данные"

        headers = list(columns.keys())
        ws.append(headers)

        max_len = max((len(v) for v in columns.values()), default=0)
        for i in range(max_len):
            row = [
                cols[i] if i < len(cols) else None
                for cols in columns.values()
            ]
            ws.append(row)

        wb.save(path)

"""
Виджет matplotlib для интеграции графиков в Qt
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QDialog, QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


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
    
    def __init__(self, parent=None, title="График", figsize=(12, 8)):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(int(figsize[0] * 100), int(figsize[1] * 100))
        
        # Виджет matplotlib
        self.plot_widget = MatplotlibWidget(self, figsize=figsize)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.plot_widget)
    
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

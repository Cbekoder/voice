import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import QTimer

class VisualizerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Sound Visualizer')
        self.setGeometry(100, 100, 800, 600)

        self.canvas = SoundCanvas(self)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_visualization)
        self.timer.start(50)  # Update every 50 milliseconds

    def update_visualization(self):
        self.canvas.update_plot()

class SoundCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure()
        super().__init__(fig)
        self.setParent(parent)

        self.ax = fig.add_subplot(111)
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 255)

        self.WIDTH = 100
        self.buffer_length_alt = 64
        self.data_array_alt = np.zeros(self.buffer_length_alt)

    def update_plot(self):
        self.data_array_alt = np.random.rand(self.buffer_length_alt) * 255  # Replace this with your actual data

        self.ax.clear()
        bar_width = (self.WIDTH / self.buffer_length_alt)
        x = 0

        for i in range(self.buffer_length_alt):
            bar_height = self.data_array_alt[i]

            color = (bar_height + 100, 50, 50)
            self.ax.bar(x, bar_height / 2, bar_width, color=[c / 255 for c in color])

            x += bar_width + 1

        self.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VisualizerApp()
    window.show()
    sys.exit(app.exec_())

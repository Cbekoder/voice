import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget
import pyqtgraph as pg
import numpy as np
import pyaudio


class SoundFrequencyPlotter(QMainWindow):
    def __init__(self):
        super(SoundFrequencyPlotter, self).__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Sound Frequency Plotter')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Create a QGraphicsView with a QGraphicsScene
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        layout.addWidget(self.view)

        # Create a PlotWidget for real-time plotting
        self.plot_widget = pg.PlotWidget()
        self.plot_item = self.plot_widget.getPlotItem()
        self.plot_item.setLabels(title='Sound Frequency', left='Amplitude', bottom='Time')
        layout.addWidget(self.plot_widget)

        # Configure the microphone input
        self.p = pyaudio.PyAudio()
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100

        # Create a numpy array for storing audio data
        self.audio_data = np.zeros(self.CHUNK)

        # Create a CurveItem for plotting
        self.curve = self.plot_item.plot(pen='y')
        self.plot_data = np.zeros(self.CHUNK)

        # Start the microphone stream
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
            stream_callback=self.update_plot
        )

        self.stream.start_stream()

    def update_plot(self, in_data, frame_count, time_info, status):
        # Convert binary data to numpy array
        data = np.frombuffer(in_data, dtype=np.int16)

        # Update the plot data
        self.plot_data = np.concatenate((self.plot_data[len(data):], data))

        # Update the curve with new data
        self.curve.setData(self.plot_data)

        return in_data, pyaudio.paContinue


def main():
    app = QApplication(sys.argv)
    window = SoundFrequencyPlotter()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

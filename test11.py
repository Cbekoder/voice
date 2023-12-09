import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sounddevice as sd
import matplotlib.pyplot as plt

class AudioRecorderApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Audio Recorder')
        self.setGeometry(100, 100, 800, 600)

        self.record_button = QPushButton('Record', self)
        self.record_button.clicked.connect(self.toggle_recording)

        self.play_button = QPushButton('Play', self)
        self.play_button.clicked.connect(self.play_recorded_audio)

        self.canvas = FrequencyCanvas(self)

        layout = QVBoxLayout()
        layout.addWidget(self.record_button)
        layout.addWidget(self.play_button)
        layout.addWidget(self.canvas)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.recording = False
        self.recorder = None

    def toggle_recording(self):
        self.recording = not self.recording
        if self.recording:
            self.record_button.setText('Stop Recording')
            self.start_recording()
        else:
            self.record_button.setText('Record')
            self.stop_recording()

    def start_recording(self):
        self.recorder = []
        sd.InputStream(callback=self.callback).start()

    def stop_recording(self):
        sd.stop()

    def callback(self, indata, frames, time, status):
        if status:
            print(status, flush=True)
        if self.recording:
            self.recorder.extend(indata.copy())
            self.canvas.update_plot(indata)

    def play_recorded_audio(self):
        if self.recorder is not None:
            audio_data = np.array(self.recorder)
            sd.play(audio_data, samplerate=44100)
            sd.wait()

class FrequencyCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig, self.ax = plt.subplots()
        super().__init__(fig)
        self.setParent(parent)

        self.ax.set_xlim(0, 1000)
        self.ax.set_ylim(0, 1)

    def update_plot(self, audio_data):
        self.ax.clear()
        self.ax.specgram(audio_data[:, 0], Fs=44100, cmap='viridis')
        self.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AudioRecorderApp()
    window.show()
    sys.exit(app.exec_())

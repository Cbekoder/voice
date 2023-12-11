import sys
import os
import threading
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import pyaudio
import wave
import subprocess
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QPen
from pyqtgraph import PlotWidget, setConfigOptions

class SpectrogramWidget(PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.img = None
        self.init_ui()

    def init_ui(self):
        self.plotItem.showGrid(True, True, alpha=0.5)
        self.getPlotItem().setLabel("left", "Frequency", units="Hz")
        self.getPlotItem().setLabel("bottom", "Time", units="s")

    def update_plot(self, data):
        img = np.fft.fft2(data)
        img = np.fft.fftshift(img)
        img = np.abs(img)
        img = 10 * np.log10(img + 1)

        if self.img is None:
            self.img = self.imageItem.setImage(img, autoLevels=False)
        else:
            self.img.setImage(img)

class RecorderApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Audio Recorder GUI")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.recorder = Recorder()

        self.init_ui()

    def init_ui(self):
        start_button = QPushButton("Start", self)
        start_button.clicked.connect(self.recorder.start)

        stop_button = QPushButton("Stop", self)
        stop_button.clicked.connect(self.recorder.stop)

        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_file)

        convert_button = QPushButton("Convert to MP3", self)
        convert_button.clicked.connect(self.convert_to_mp3)

        delete_button = QPushButton("Delete", self)
        delete_button.clicked.connect(self.delete_file)

        file_name_label = QLabel("File Name:", self)
        self.file_name_input = QLineEdit(self)

        hbox = QHBoxLayout()
        hbox.addWidget(file_name_label)
        hbox.addWidget(self.file_name_input)

        vbox = QVBoxLayout(self.central_widget)
        vbox.addWidget(start_button)
        vbox.addWidget(stop_button)
        vbox.addWidget(save_button)
        vbox.addWidget(convert_button)
        vbox.addWidget(delete_button)
        vbox.addLayout(hbox)

        self.spectrogram_widget = SpectrogramWidget(self.central_widget)
        vbox.addWidget(self.spectrogram_widget)

    def save_file(self):
        file_name = self.file_name_input.text()
        if not file_name:
            file_name = "recording"
        self.recorder.save(file_name + ".wav")

    def convert_to_mp3(self):
        file_name = self.file_name_input.text()
        if not file_name:
            file_name = "recording"
        self.recorder.wav_to_mp3(file_name + ".wav")

    def delete_file(self):
        file_name = self.file_name_input.text()
        if not file_name:
            file_name = "recording"
        self.recorder.delete(file_name + ".wav")

    def closeEvent(self, event):
        self.recorder.stop()
        event.accept()

class Recorder:
    def __init__(self, chunk=1024, channels=2, rate=44100):
        self.CHUNK = chunk
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = channels
        self.RATE = rate
        self._running = False
        self._frames = []
        self.spectrogram_data = np.array([])

    def start(self):
        if not self._running:
            self._running = True
            threading.Thread(target=self.__recording).start()

    def __recording(self):
        p = pyaudio.PyAudio()
        stream = p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )

        while self._running:
            data = stream.read(self.CHUNK)
            self._frames.append(data)
            np_data = np.frombuffer(data, dtype=np.int16)
            self.spectrogram_data = np.append(self.spectrogram_data, np_data)
            self.spectrogram_data = self.spectrogram_data[-10000:]  # Keep the last 10000 samples

        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop(self):
        self._running = False

    def save(self, filename):
        p = pyaudio.PyAudio()
        wf = wave.open(filename, "wb")
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b"".join(self._frames))
        wf.close()

    @staticmethod
    def delete(filename):
        os.remove(filename)

    @staticmethod
    def wav_to_mp3(wav):
        mp3 = wav[:-3] + "mp3"
        if os.path.isfile(mp3):
            Recorder.delete(mp3)
        subprocess.call('ffmpeg -i "' + wav + '" "' + mp3 + '"')


def main():
    app = QApplication(sys.argv)
    window = RecorderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

# working in GUI


import sys
import time
import os
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QLineEdit, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import pyaudio
import wave
import subprocess

class RecorderApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Audio Recorder GUI')
        self.setGeometry(100, 100, 400, 200)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.recorder = Recorder()

        self.init_ui()

    def init_ui(self):
        start_button = QPushButton('Start', self)
        start_button.clicked.connect(self.recorder.start)

        stop_button = QPushButton('Stop', self)
        stop_button.clicked.connect(self.recorder.stop)

        save_button = QPushButton('Save', self)
        save_button.clicked.connect(self.save_file)

        convert_button = QPushButton('Convert to MP3', self)
        convert_button.clicked.connect(self.convert_to_mp3)

        delete_button = QPushButton('Delete', self)
        delete_button.clicked.connect(self.delete_file)

        file_name_label = QLabel('File Name:', self)
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

    def start(self):
        if not self._running:
            threading.Thread(target=self.__recording).start()

    def __recording(self):
        self._running = True
        self._frames = []
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        while self._running:
            data = stream.read(self.CHUNK)
            self._frames.append(data)
        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop(self):
        self._running = False

    def save(self, filename):
        print("Saving")
        p = pyaudio.PyAudio()
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self._frames))
        wf.close()
        print("Saved")

    @staticmethod
    def delete(filename):
        os.remove(filename)

    @staticmethod
    def wav_to_mp3(wav):
        mp3 = wav[:-3] + "mp3"
        if os.path.isfile(mp3):
            Recornder.delete(mp3)
        subprocess.call('ffmpeg -i "' + wav + '" "' + mp3 + '"')


def main():
    app = QApplication(sys.argv)
    window = RecorderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

import sys
import os
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QLineEdit, \
    QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtGui import QPainter, QPen
import pyaudio
import wave
import subprocess

class RecorderApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Audio Recorder GUI')
        self.setGeometry(100, 100, 600, 600)

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

        self.canvas_label = QLabel(self)
        self.canvas_label.setAlignment(Qt.AlignCenter)
        self.canvas_label.setFixedSize(400, 200)

        self.visual_thread = threading.Thread(target=self.update_visualization)
        self.visual_thread.start()

        vbox = QVBoxLayout(self.central_widget)
        vbox.addWidget(self.canvas_label)
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

    def update_visualization(self):
        while True:
            if self.recorder.visual_data:
                image = self.create_visualization_image(self.recorder.visual_data)
                pixmap = QPixmap.fromImage(image)
                self.canvas_label.setPixmap(pixmap)
            else:
                self.canvas_label.clear()

    def create_visualization_image(self, visual_data):
        width, height = 400, 200
        image = QImage(width, height, QImage.Format_RGB32)
        image.fill(Qt.white)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(Qt.black)
        pen.setWidth(2)
        painter.setPen(pen)

        # Draw visualization based on visual_data
        for i in range(len(visual_data) - 1):
            x1 = int(i / len(visual_data) * width)
            y1 = int((1 - (visual_data[i] / 128.0)) * height / 2)
            x2 = int((i + 1) / len(visual_data) * width)
            y2 = int((1 - (visual_data[i + 1] / 128.0)) * height / 2)
            painter.drawLine(x1, y1, x2, y2)

        painter.end()
        return image


class Recorder:
    def __init__(self, chunk=1024, channels=2, rate=44100):
        self.CHUNK = chunk
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = channels
        self.RATE = rate
        self._running = False
        self._frames = []
        self.visual_data = []

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
            self.update_visual_data(data)
        stream.stop_stream()
        stream.close()
        p.terminate()

    def update_visual_data(self, data):
        visual_data = list(data)
        self.visual_data = visual_data

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
            Recorder.delete(mp3)
        subprocess.call('ffmpeg -i "' + wav + '" "' + mp3 + '"')


def main():
    app = QApplication(sys.argv)
    window = RecorderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

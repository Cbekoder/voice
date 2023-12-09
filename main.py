import sys
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import sounddevice as sd
import numpy as np

MAX_FRAMES = 1000  # Adjust this value

class AudioRecorder(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.chunk = 1024
        self.sample_rate = 44100
        self.channels = 1
        self.audio_frames = []

        self.init_ui()

    def init_ui(self):
        self.record_button = QtWidgets.QPushButton('Record', self)
        self.record_button.clicked.connect(self.start_recording)

        self.stop_button = QtWidgets.QPushButton('Stop', self)
        self.stop_button.clicked.connect(self.stop_recording)

        self.play_button = QtWidgets.QPushButton('Play', self)
        self.play_button.clicked.connect(self.play_audio)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.record_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.play_button)
        self.setLayout(layout)

    def start_recording(self):
        self.audio_frames = []  # Reset frames when starting recording
        with sd.InputStream(callback=self.callback):
            sd.sleep(10000)  # Adjust the recording duration as needed

    def stop_recording(self):
        sd.stop()

    def play_audio(self):
        if self.audio_frames:
            audio_data = np.concatenate(self.audio_frames, axis=0)
            sd.play(audio_data, self.sample_rate)
            sd.wait()

    def callback(self, indata, frames, time, status):
        if status:
            print('Error:', status)
        else:
            data = indata.copy()
            if len(self.audio_frames) < MAX_FRAMES:
                self.audio_frames.append(data)
            else:
                self.audio_frames.pop(0)
                self.audio_frames.append(data)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    recorder = AudioRecorder()
    recorder.show()
    sys.exit(app.exec_())

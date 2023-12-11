import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QListWidget
from PyQt5.QtMultimedia import QAudioRecorder, QMediaRecorder, QMediaPlayer
from PyQt5.QtCore import QUrl

class AudioRecorderApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Audio Recorder')
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.audio_recorder = QAudioRecorder()
        self.audio_recorder.setAudioInput('default')
        self.audio_recorder.setAudioOutput('default')

        self.record_button = QPushButton('Record', self)
        self.record_button.clicked.connect(self.start_recording)

        self.stop_button = QPushButton('Stop', self)
        self.stop_button.clicked.connect(self.stop_recording)

        self.flag_button = QPushButton('Flag', self)
        self.flag_button.clicked.connect(self.flag_recording)

        self.recordings_list = QListWidget(self)

        self.play_button = QPushButton('Play', self)
        self.play_button.clicked.connect(self.play_recording)

        self.audio_player = QMediaPlayer(self)
        self.audio_player.stateChanged.connect(self.update_play_button)

        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.record_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.flag_button)
        layout.addWidget(self.recordings_list)
        layout.addWidget(self.play_button)

        self.recording_flag = False
        self.recordings = []

    def start_recording(self):
        if not self.recording_flag:
            output_path = os.path.join(os.getcwd(), 'recordings', 'output.wav')
            self.audio_recorder.setOutputLocation(QUrl.fromLocalFile(output_path))
            self.audio_recorder.record()
            self.recording_flag = True

    def stop_recording(self):
        if self.recording_flag:
            self.audio_recorder.stop()
            output_file = self.audio_recorder.outputLocation().toLocalFile()
            self.recordings_list.addItem(os.path.basename(output_file))
            self.recordings.append(output_file)
            self.recording_flag = False

    def flag_recording(self):
        if self.recording_flag:
            self.stop_recording()
            self.start_recording()

    def play_recording(self):
        selected_item = self.recordings_list.currentItem()
        if selected_item:
            file_path = self.recordings[self.recordings_list.row(selected_item)]
            self.audio_player.setMedia(QUrl.fromLocalFile(file_path))
            self.audio_player.play()

    def update_play_button(self, state):
        if state == QMediaPlayer.StoppedState:
            self.play_button.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    window = AudioRecorderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

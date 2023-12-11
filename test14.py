import sys
import pyaudio
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog
from pyqtgraph import PlotWidget, setConfigOptions
import wave

class AudioRecorderApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.recording = False
        self.recorder = None
        self.amplitude_threshold = 0.09  # Adjust the threshold as needed
        self.silence_duration = 2  # Adjust the duration as needed (in seconds)
        self.silence_counter = 0
        self.volume_factor = 0.5

        self.playback_active = False
        self.playback_data = None

        self.setWindowTitle("Audio Recorder")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.plot_widget = PlotWidget()
        self.plot_widget.setLabel('left', 'Amplitude')
        self.plot_widget.setLabel('bottom', 'Time')
        self.plot_data = self.plot_widget.plot(pen='g')

        self.record_button = QPushButton("Record")
        self.record_button.clicked.connect(self.toggle_recording)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_recorded_audio)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_recorded_audio)

        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        layout.addWidget(self.record_button)
        layout.addWidget(self.play_button)
        layout.addWidget(self.save_button)

        self.central_widget.setLayout(layout)

        self.init_audio()

        self.recorded_data = None

    def init_audio(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=44100,
                                  input=True,
                                  frames_per_buffer=1024,
                                  stream_callback=self.audio_callback)

    def toggle_recording(self):
        if not self.recording:
            self.recording = True
            self.recorder = np.array([])
            self.record_button.setText("Stop")
            self.play_button.setEnabled(False)
            self.save_button.setEnabled(False)
            self.silence_counter = 0
        else:
            self.recording = False
            self.record_button.setText("Record")
            self.play_button.setEnabled(True)
            self.save_button.setEnabled(True)
            self.plot_data.setData(self.recorder)
            self.recorded_data = self.recorder.copy()
            self.recorder = None

    def play_recorded_audio(self):
        if self.recorded_data is not None:
            self.playback_active = True

            # Adjust the volume of the recorded audio
            adjusted_data = (self.recorded_data * self.volume_factor).astype(np.int16)

            playback = pyaudio.PyAudio()
            playback_stream = playback.open(format=pyaudio.paInt16,
                                           channels=1,
                                           rate=44100,
                                           output=True)

            self.playback_data = adjusted_data
            playback_stream.write(self.playback_data.tobytes())

            playback_stream.stop_stream()
            playback_stream.close()
            playback.terminate()

            self.playback_active = False

    def save_recorded_audio(self):
        if self.recorded_data is not None:
            file_dialog = QFileDialog(self)
            file_path, _ = file_dialog.getSaveFileName(self, "Save Audio File", "", "WAV Files (*.wav);;All Files (*)")

            if file_path:
                with wave.open(file_path, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(44100)
                    wf.writeframes(self.recorded_data.tobytes())

    def audio_callback(self, in_data, frame_count, time_info, status):
        if self.recording:
            data = np.frombuffer(in_data, dtype=np.int16)
            self.recorder = np.append(self.recorder, data)
            self.plot_data.setData(self.recorder[-1000:])  # Show the last 1000 samples

            amplitude = np.max(np.abs(data)) / 32768.0
            if amplitude < self.amplitude_threshold:
                self.silence_counter += 1
                if self.silence_counter >= int(44100 * self.silence_duration / 1024):
                    self.toggle_recording()
            else:
                self.silence_counter = 0

        if self.playback_active:
            return self.playback_data, pyaudio.paContinue
        else:
            return in_data, pyaudio.paContinue

    def closeEvent(self, event):
        if self.p.is_stream_active(self.stream):
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()

if __name__ == "__main__":
    setConfigOptions(antialias=True)
    app = QApplication(sys.argv)
    window = AudioRecorderApp()
    window.show()
    sys.exit(app.exec_())
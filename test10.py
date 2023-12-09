# working auto stop
import sys
import pyaudio
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from pyqtgraph import PlotWidget, setConfigOptions

class AudioRecorderApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.recording = False
        self.recorder = None
        self.amplitude_threshold = 0.09  # Adjust the threshold as needed
        self.silence_duration = 2  # Adjust the duration as needed (in seconds)
        self.silence_counter = 0

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

        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        layout.addWidget(self.record_button)

        self.central_widget.setLayout(layout)

        self.init_audio()

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
            self.silence_counter = 0
        else:
            self.recording = False
            self.record_button.setText("Record")
            self.plot_data.setData(self.recorder)
            self.recorder = None

    def audio_callback(self, in_data, frame_count, time_info, status):
        if self.recording:
            data = np.frombuffer(in_data, dtype=np.int16)
            self.recorder = np.append(self.recorder, data)
            self.plot_data.setData(self.recorder[-1000:])  # Show the last 1000 samples

            amplitude = np.max(np.abs(data)) / 32768.0
            if amplitude < self.amplitude_threshold:
                self.silence_counter += 1
                if self.silence_counter >= int(44100 * self.silence_duration / 1024):
                    # If amplitude is below threshold for the specified duration, stop recording
                    self.toggle_recording()
            else:
                self.silence_counter = 0

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

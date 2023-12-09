import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sounddevice as sd
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class AudioRecorderApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Audio Recorder')
        self.setGeometry(100, 100, 600, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.init_ui()

    def init_ui(self):
        self.record_button = QPushButton('Record', self)
        self.record_button.clicked.connect(self.toggle_recording)

        self.play_button = QPushButton('Play Recorded Voice', self)
        self.play_button.clicked.connect(self.play_recorded_voice)
        self.play_button.setEnabled(False)

        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.record_button)
        layout.addWidget(self.play_button)

        # Create the Matplotlib figure and canvas
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.recording = False
        self.audio_data = []

        self.stream = sd.InputStream(callback=self.audio_callback)

    def toggle_recording(self):
        if not self.recording:
            self.record_button.setText('Stop')
            self.recording = True
            self.audio_data = []  # Clear previous recorded data
            self.stream.start()
        else:
            self.record_button.setText('Record')
            self.recording = False
            self.stream.stop()
            self.play_button.setEnabled(True)

    def play_recorded_voice(self):
        if self.audio_data:
            sd.play(np.array(self.audio_data), samplerate=44100)

    def audio_callback(self, indata, frames, time, status):
        if self.recording:
            # Process the audio data (you can customize this part)
            self.audio_data.extend(indata.flatten())

            # Update the canvas with the sound amplitude
            self.ax.clear()
            self.ax.plot(np.linspace(0, len(self.audio_data) / 44100, len(self.audio_data)), self.audio_data)
            self.ax.set_xlabel('Time (s)')
            self.ax.set_ylabel('Amplitude')
            self.canvas.draw()

    def closeEvent(self, event):
        self.stream.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = AudioRecorderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

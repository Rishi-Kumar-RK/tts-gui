import os
import sys
import traceback
import pyttsx3
from datetime import datetime
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider, QLabel, QToolButton, QTextEdit, QPushButton, QFileDialog, QComboBox, QMessageBox
from PyQt5.uic import loadUi

directory = os.path.dirname(__file__)
speaker_icon = os.path.join(directory, "UI", "speaker.png")

class TTSWindow(QMainWindow):
    def __init__(self):
        super(TTSWindow, self).__init__()
        ui_file = os.path.join(directory, "UI", "TTS.ui")
        loadUi(ui_file, self)

        self.engine = pyttsx3.init()
        self.set_default_values()
        self.setup_events()
        self.Status.setText(f"Ready")

    def set_default_values(self):
        
        self.Status.setText(f"Idle")
        self.Voice: QComboBox
        self.Rate: QSlider
        self.Volume: QSlider
        self.RateStatus: QLabel
        self.VolumeStatus: QLabel
        self.Status: QLabel
        self.InputFile: QTextEdit
        self.InputText: QTextEdit
        self.OutputFolder: QTextEdit
        self.InputFileBrowse: QToolButton
        self.OutputFolderBrowse: QToolButton
        self.Generate: QPushButton
        self.Preview: QToolButton

        self.rate = 120
        self.Rate.setValue(self.rate)
        self.RateStatus.setText(str(self.rate))
        self.volume = 1
        self.Volume.setValue(self.volume * 10)
        self.VolumeStatus.setText(str(self.volume))

        self.InputFile.setReadOnly(True)
        self.OutputFolder.setReadOnly(True)
        self.OutputFolder.setPlaceholderText(r"C:\temp")

        self.Preview.setIcon(QIcon(speaker_icon))

        self.Status.setText(f"Listing voices...")
        self.list_voices()

    def setup_events(self):
        self.Voice.currentIndexChanged.connect(self.update_voice)
        self.InputFileBrowse.clicked.connect(self.input_file_browse)
        self.OutputFolderBrowse.clicked.connect(self.output_folder_browse)
        self.Rate.valueChanged.connect(self.update_rate)
        self.Volume.valueChanged.connect(self.update_volume)
        self.Generate.clicked.connect(self.generate)
        self.Preview.clicked.connect(self.preview_voice)

    def close_window(self):
        self.close()

    def list_voices(self):
        self.voices = self.engine.getProperty('voices')
        voice_names = []
        for voice in self.voices:
            voice_names.append(voice.name)
        
        self.Voice.addItems(voice_names)
        self.Voice.setCurrentIndex(0)
        self.voice = 0

    def update_voice(self, index):
        self.voice = index
        return
    
    def input_file_browse(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Self Input text file", "", "text(*.txt)")
        if file_path:
            self.InputFile.setText(file_path)

        return
    
    def output_folder_browse(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select output folder path")
        if folder_path:
            self.OutputFolder.setText(folder_path)

        return
    
    def update_rate(self, value):
        self.rate = value
        self.RateStatus.setText(str(value))

        return
    
    def update_volume(self, value):
        decimal_value = value / 10.0
        self.volume = decimal_value
        self.VolumeStatus.setText(f"{decimal_value:.1f}")

        return
    
    def preview_voice(self):
        voice_id = self.voices[self.voice].id
        self.engine.setProperty("rate", self.rate)
        self.engine.setProperty("volume", self.volume)
        self.engine.setProperty("voice", voice_id)

        self.Status.setText("Previewing voice...")
        self.engine.say("Hi! This is test.")
        self.engine.runAndWait()
        self.Status.setText("Ready")

        return
    
    def generate(self):
        
        try:
            voice_id = self.voices[self.voice].id
            input_text_filepath = self.InputFile.toPlainText()
            input_text_box = self.InputText.toPlainText()

            input_texts = []
            valid = True
            if input_text_filepath:
                with open(input_text_filepath, "r") as file:
                    lines = file.readlines()
                    input_texts = [line.strip() for line in lines]
            elif input_text_box:
                input_texts.append(input_text_box)
            else:
                valid = False

            if valid:
                output_folder = self.OutputFolder.toPlainText()
                if not output_folder:
                    output_folder = r"C:\temp"

                self.Status.setText(f"Generating voice...")
                self.tts_generate(self.rate, self.volume, voice_id, input_texts, output_folder)
                self.Status.setText(f"Generation completed")
            else:
                self.Status.setText(f"Provide input file or text for generation!")
        except Exception as e:
            self.Status.setText(f"Generation error: {str(e)}")
        return
    
    def tts_generate(self, rate, volume, voice_id, input_texts, output_folder):

        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)
        self.engine.setProperty("voice", voice_id)
        os.makedirs(output_folder, exist_ok=True)

        for i,text in enumerate(input_texts,1):
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d_%H-%M-%S")
            current_file_path = os.path.join(output_folder, f"voice_{i}_{formatted_time}.mp3")

            self.engine.save_to_file(text, current_file_path)
            self.engine.runAndWait()
            self.Status.setText(f"Generating voice {i}...")

        return
    
def error_popup(message):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("An Error Occurred")
    msg_box.setText("An unexpected error occurred.")
    msg_box.setInformativeText(str(message))
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()

def exception_hook(exctype, value, tb):
    error_message = "".join(traceback.format_exception(exctype, value, tb))
    error_popup(value)
    
def tts_main():
    sys.excepthook = exception_hook
    app = QApplication(sys.argv)
    window = TTSWindow()
    window.show()

    # Run the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    tts_main()
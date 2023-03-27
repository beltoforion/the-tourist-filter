from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from detector.yoloonnxdetector import *
from ui.image_dialog import *


class FilterWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, detector : YoloOnnxDetector, input_folder):
        super().__init__()
        self.__detector = detector
        self.__input_folder = input_folder
        self.__output_file = None

    @property
    def output_file(self):
        return self.__output_file
    
    def run(self):
        self.__output_file = self.__detector.process_folder(pathlib.Path(self.__input_folder))
#        ImageDialog(self.__output_file).exec()
        self.finished.emit()
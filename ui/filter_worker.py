from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from detector.yoloonnxdetector import *
from ui.image_dialog import *


class FilterThread(QThread):
    finished = pyqtSignal()
    success = pyqtSignal(str)
    failure = pyqtSignal(Exception)    

    def __init__(self, detector : YoloOnnxDetector, input_folder : str, method : RemovalMethod):
        super().__init__()
        self.__detector = detector
        self.__input_folder = input_folder
        self.__output_file = None
        self.__method = method


    @property
    def output_file(self):
        return self.__output_file


    def run(self):
        try:
            self.__detector.method = self.__method
            self.__output_file = self.__detector.process_folder(pathlib.Path(self.__input_folder))
            self.success.emit(self.__output_file)
        except Exception as exc:
            self.failure.emit(exc)
        finally:
            self.finished.emit()


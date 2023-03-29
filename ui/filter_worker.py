from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from detector.yoloonnxdetector import *
from ui.image_dialog import *


class FilterWorker(QObject):
    finished = pyqtSignal(str)

    def __init__(self, detector : YoloOnnxDetector, input_folder : str, method : RemovalMethod):
        super().__init__()
        self.__detector = detector
        self.__input_folder = input_folder
        self.__method = method

    def run(self):
        self.__detector.method = self.__method
        outputfile = self.__detector.process_folder(pathlib.Path(self.__input_folder))

        ImageDialog(outputfile).exec()
        self.finished.emit(outputfile)
import os

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from detector.yoloonnxdetector import *
from detector.displaybase import DisplayBase

from ui.filter_worker import FilterWorker
from ui.image_dialog import *

class UiController(DisplayBase):
    def __init__(self, detector : YoloOnnxDetector):
        detector.setDisplay(self)

        self.__buttonFont = QFont("Arial", 14)
        self.__textFont = QFont("Arial", 12)

        self._app = QApplication([])
        self._window = QWidget() 

        self._window.setWindowTitle("Magic Stack - The Tourist Filter")


        self._buttonMedian = QRadioButton('Median')
        self._buttonCut = QRadioButton('Cut')
        self._buttonCutAndMedian = QRadioButton('Cut and Median')
        self._buttonNoiseAndMedian = QRadioButton('Noise and Median')
        self._buttonInpaintAndMedian = QRadioButton('Inpaint and Median')

        self._buttonStart = QPushButton("Start")
        self._buttonStart.setEnabled(False)

#        self._image = QImage(800, 600, QImage.Format.Format_RGB32)
        self._image = QImage("./assets/images/title.jpg")

        self._input_folder = None
        self._detector = detector
        self._method = detector.method

    @property
    def input_folder(self):
        return self._input_folder

    @input_folder.setter
    def input_folder(self, value):
        self._input_folder = value
        self._buttonStart.setEnabled(os.path.exists(self._input_folder))

    @property
    def _method(self):
        if self._buttonMedian.isChecked():
            return RemovalMethod.MEDIAN
        elif self._buttonCut.isChecked():
            return RemovalMethod.CUT
        elif self._buttonCutAndMedian.isChecked:
            return RemovalMethod.CUT_AND_MEDIAN
        elif self._buttonNoiseAndMedian.isChecked:
            return RemovalMethod.NOISE_AND_MEDIAN
        elif self._buttonInpaintAndMedian.isChecked:
            return RemovalMethod.INPAINT_AND_MEDIAN


    @_method.setter
    def _method(self, method):
        if method is None:
            method = RemovalMethod.INPAINT_AND_MEDIAN

        self._detector.method = method
        self._buttonMedian.setChecked(method==RemovalMethod.MEDIAN)
        self._buttonCut.setChecked(method==RemovalMethod.CUT)
        self._buttonCutAndMedian.setChecked(method==RemovalMethod.CUT_AND_MEDIAN)
        self._buttonNoiseAndMedian.setChecked(method==RemovalMethod.NOISE_AND_MEDIAN)
        self._buttonInpaintAndMedian.setChecked(method==RemovalMethod.INPAINT_AND_MEDIAN)


    def on_start(self):
        self._buttonStart.setEnabled(False)

        self.__thread = QThread()
        self.__worker = FilterWorker(self._detector, self._input_folder)
        self.__worker.moveToThread(self.__thread)#

        self.__thread.started.connect(self.__worker.run)
        self.__worker.finished.connect(self.__thread.quit)
        self.__worker.finished.connect(self.__worker.deleteLater)
        self.__thread.finished.connect(self.__thread.deleteLater)

        self.__thread.start()

        self.__thread.finished.connect(
            lambda: self._buttonStart.setEnabled(True)
        )


    def on_select_image_folder(self):
        dlg = QFileDialog()
        self.input_folder = dlg.getExistingDirectory(None, "Select Folder")
        
        print(f"selected folder: {self.input_folder}")        


    def display_image(self, image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
        self.__label_image.setPixmap(QPixmap.fromImage(image).scaled(self.__label_image.size(), Qt.AspectRatioMode.KeepAspectRatio))


    def show(self):
        gridLayout = QGridLayout()
        gridLayout.setContentsMargins(5, 5, 5, 5)
        gridLayout.setColumnStretch(0, 1)
        gridLayout.setColumnStretch(1, 1)
        gridLayout.setColumnStretch(2, 1)
        gridLayout.setRowStretch(1, 1)

        titleImage = QPixmap("./assets/images/title.jpg")
        title = QLabel()
        title.setPixmap(titleImage)
        title.setMargin(0)

        #
        #
        #

        groupOpen = QGroupBox("Step 1: Open Input Stack")
        groupOpenLayout = QVBoxLayout()
        groupOpenLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        groupOpen.setLayout(groupOpenLayout)
        button = QPushButton("Select Image Folder")
        button.setMaximumSize(250, 80)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        button.setFont(self.__buttonFont)
        button.clicked.connect(self.on_select_image_folder)
        groupOpenLayout.addWidget(button)

        #
        #
        #

        groupSelect = QGroupBox("Step 2: Select Method") 
        groupSelectLayout = QVBoxLayout()
        groupSelectLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        groupSelect.setLayout(groupSelectLayout)

        group = QGroupBox("Select Method") 
        group.setMaximumSize(200, 150)
        group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        groupLayout = QVBoxLayout()
        groupLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        groupSelectLayout.addWidget(group)
        group.setLayout(groupLayout)

        buttonGroup = QButtonGroup()
        buttonGroup.addButton(self._buttonMedian)
        buttonGroup.addButton(self._buttonCut)
        buttonGroup.addButton(self._buttonCutAndMedian)        
        buttonGroup.addButton(self._buttonNoiseAndMedian)        
        buttonGroup.addButton(self._buttonInpaintAndMedian)        

        groupLayout.addWidget(self._buttonMedian)
        groupLayout.addWidget(self._buttonCut)
        groupLayout.addWidget(self._buttonCutAndMedian)
        groupLayout.addWidget(self._buttonNoiseAndMedian)
        groupLayout.addWidget(self._buttonInpaintAndMedian)                                

        #
        #
        #

        groupStart = QGroupBox("Step 3: Start") 
        groupStartLayout = QVBoxLayout()
        groupStartLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        groupStart.setLayout(groupStartLayout)
        self._buttonStart.setMaximumSize(250, 80)
        self._buttonStart.setFont(self.__buttonFont)
        self._buttonStart.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._buttonStart.clicked.connect(self.on_start)
        groupStartLayout.addWidget(self._buttonStart)

        #
        # Image Label
        #

        self.__label_image = QLabel()
        self.__label_image.setPixmap(QPixmap.fromImage(self._image))
        self.__label_image.setScaledContents(False)
        self.__label_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        gridLayout.addWidget(groupOpen, 0, 0)
        gridLayout.addWidget(groupSelect, 0, 1)
        gridLayout.addWidget(groupStart, 0, 2)
        gridLayout.addWidget(self.__label_image, 1, 0, 1, 3)

        self._window.setLayout(gridLayout)
        self._window.show()
        self._app.exec()
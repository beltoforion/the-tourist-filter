from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from detector.yoloonnxdetector import *


class UiController:
    def __init__(self, detector : YoloOnnxDetector):
        self._buttonFont = QFont("Arial", 14)
        self._textFont = QFont("Arial", 12)

        self._app = QApplication([])
        self._window = QWidget()
#        self._window.setGeometry(100,100, 800, 400)
        self._window.setWindowTitle("Magic Stack - The Tourist Filter")
        self._window.setFixedSize(1000,400)

        self._buttonMedian = QRadioButton('Median')
        self._buttonCut = QRadioButton('Cut')
        self._buttonCutAndMedian = QRadioButton('Cut and Median')
        self._buttonNoiseAndMedian = QRadioButton('Noise and Median')
        self._buttonInpaintAndMedian = QRadioButton('Inpaint and Median')

        self._input_folder = None
        self._detector = detector
        self._method = detector.method


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
        self._detector.process_folder(pathlib.Path(self._input_folder))


    def on_select_image_folder(self):
        dlg = QFileDialog()
        self._input_folder = dlg.getExistingDirectory(None, "Select Folder")
        
        self.label_input.setText(f"Input Folder: {self._input_folder}")
        print(f"selected folder: {self._input_folder}")        


    def show(self):
        gridLayout = QGridLayout()
        gridLayout.setContentsMargins(5, 5, 5, 5)
        gridLayout.setColumnStretch(0, 1)
        gridLayout.setColumnStretch(1, 1)
        gridLayout.setColumnStretch(2, 1)

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
        button.setFont(self._buttonFont)
        button.clicked.connect(self.on_select_image_folder)
        groupOpenLayout.addWidget(button)

        self.label_input = QLabel()
        self.label_input.setText(f"folder: {self._input_folder}")
        self.label_input.setFont(self._textFont)
        self.label_input.setFixedHeight(20)
        groupOpenLayout.addWidget(self.label_input)

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
        buttonStart = QPushButton("Start")
        buttonStart.setMaximumSize(250, 80)
        buttonStart.setFont(self._buttonFont)
        buttonStart.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        buttonStart.clicked.connect(self.on_start)
        groupStartLayout.addWidget(buttonStart)

        gridLayout.addWidget(title, 0, 0, 1, 3)
        gridLayout.addWidget(groupOpen, 1, 0)
        gridLayout.addWidget(groupSelect, 1, 1)
        gridLayout.addWidget(groupStart, 1, 2)

        self._window.setLayout(gridLayout)
        self._window.show()
        self._app.exec()
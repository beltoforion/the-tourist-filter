import sys

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


class ImageDialog(QDialog):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle(f"Image: {file_path}")
        
        # Load the image from file
        self.image = QImage(file_path)
        
        # Create a label widget to display the image
        self.label = QLabel(self)
        self.label.setPixmap(QPixmap.fromImage(self.image).scaledToWidth(1000))
        
        # Create a layout for the dialog window and add the label widget to it
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)


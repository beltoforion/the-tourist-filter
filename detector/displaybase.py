from abc import ABC, abstractmethod
import cv2

class DisplayBase(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def display_image(self, image):
        pass


class NullDisplay(DisplayBase):
    def display_image(self, image):
        pass


class OpenCvDisplay(DisplayBase):
    def display_image(self, image):
        cv2.imshow("Image", image)
        cv2.waitKey(1)

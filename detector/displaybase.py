from abc import ABC, abstractmethod


class DisplayBase(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def display_image(self, image):
        pass
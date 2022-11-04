from cv2 import CV_32F, CV_8U
import numpy as np
import time
import cv2
import random 

from abc import ABC, abstractmethod

class DetectorBase(ABC):
    def __init__(self, name):
        self._name = name

    def start(self):
        self._mask = None
        self._mask_sum = None
        self._mask_global = None
        self._image_filtered = None
        self._perc_complete = 0
        self._image_index = 0
        self.start_impl()

    def finish(self):
        return self.finish_impl()

    @abstractmethod
    def restart_requested(self):
        return False

    @abstractmethod
    def finish_impl(self):
        pass

    @property
    def filtered_image(self):
        return self._image_filtered

    @property
    @abstractmethod
    def name_detailed(self):
        pass

    @property
    def name(self):
        return self._name

    def next_image(self, image):
        if self._mask is None:
            self._mask = np.zeros(image.shape[:2], dtype="uint8")
            self._mask_global = np.zeros(image.shape[:2], dtype="uint8")
            self._mask_sum = np.zeros(image.shape[:2], dtype="int")
            
        if self._image_filtered is None:
            self._image_filtered = image.copy()

        self._image_index += 1
        self.next_image_impl(image)

        # Compute heat map by summing up all masks
        self._mask_sum[:] += 255 - self._mask[:]

        # prepare display
        height, width, _ = image.shape                  
        display_scale = 500/width

        # compute normalized heat map
        heatmap = cv2.normalize(self._mask_sum, None, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_GRAY2BGR)

        images_left = np.vstack((image, self._image_filtered[:,:,0:3]))
        images_right = np.vstack((heatmap, cv2.cvtColor(self._mask_global, cv2.COLOR_GRAY2BGR)))
        images_4x4 = np.hstack((images_left, images_right))
        cv2.imshow('Images', cv2.resize(images_4x4, (int(2*display_scale*width), int(2*display_scale*height))))
        cv2.waitKey(1)

        non_zero_count = cv2.countNonZero(self._mask_global)  
        self._perc_complete = 100 * non_zero_count / (width*height)
        print(f'image {self._image_index}: remaining pixels associated with people: {100-self._perc_complete:.3f} %')

    @abstractmethod
    def next_image_impl(self, image):
        pass

    @abstractmethod
    def detect(self, img):
        pass

    def _add_transparent_image(self, background, foreground, x_offset=None, y_offset=None):
        bg_h, bg_w, bg_channels = background.shape
        fg_h, fg_w, fg_channels = foreground.shape

        assert bg_channels == 3, f'background image should have exactly 3 channels (RGB). found:{bg_channels}'
        assert fg_channels == 4, f'foreground image should have exactly 4 channels (RGBA). found:{fg_channels}'

        # center by default
        if x_offset is None: x_offset = (bg_w - fg_w) // 2
        if y_offset is None: y_offset = (bg_h - fg_h) // 2

        w = min(fg_w, bg_w, fg_w + x_offset, bg_w - x_offset)
        h = min(fg_h, bg_h, fg_h + y_offset, bg_h - y_offset)

        if w < 1 or h < 1: return

        # clip foreground and background images to the overlapping regions
        bg_x = max(0, x_offset)
        bg_y = max(0, y_offset)
        fg_x = max(0, x_offset * -1)
        fg_y = max(0, y_offset * -1)
        foreground = foreground[fg_y:fg_y + h, fg_x:fg_x + w]
        background_subsection = background[bg_y:bg_y + h, bg_x:bg_x + w]

        # separate alpha and color channels from the foreground image
        foreground_colors = foreground[:, :, :3]
        alpha_channel = foreground[:, :, 3] / 255  # 0-255 => 0.0-1.0

        # construct an alpha_mask that matches the image shape
        alpha_mask = np.dstack((alpha_channel, alpha_channel, alpha_channel))

        # combine the background with the overlay image weighted by alpha
        composite = background_subsection * (1 - alpha_mask) + foreground_colors * alpha_mask

        # overwrite the section of the background image that has been updated
        background[bg_y:bg_y + h, bg_x:bg_x + w] = composite
import numpy as np
import cv2

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
        self._video_out = None
        
        self.start_impl()

    def finish(self):
        if not self._video_out is None:
            self._video_out.release()

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
    def video_file(self):
        return self._video_file

    @video_file.setter
    def video_file(self, value):
        self._video_file = value

    @property
    @abstractmethod
    def name_detailed(self):
        pass

    @property
    def name(self):
        return self._name

    def next_image(self, image):
        # prepare display
        height, width, _ = image.shape                  
        ds = 700/width

        if self._mask is None:
            self._mask = np.zeros(image.shape[:2], dtype="uint8")
            self._mask_global = np.zeros(image.shape[:2], dtype="uint8")
            self._mask_sum = np.zeros(image.shape[:2], dtype="int")
            
            if not self.video_file is None:
                h, w = (int(ds*height*2), int(ds*width*2))
                self._video_out = cv2.VideoWriter(self.video_file, cv2.VideoWriter_fourcc(*'mp4v'), 2.5, (w, h))
#                self._video_out = cv2.VideoWriter(self.video_file, cv2.VideoWriter_fourcc(*'vp80'), 2.5, (w, h))

        if self._image_filtered is None:
            self._image_filtered = image.copy()

        self._image_index += 1
        self.next_image_impl(image)

        # Compute heat map by summing up all masks
        self._mask_sum[:] += 255 - self._mask[:]

        font                   = cv2.FONT_HERSHEY_DUPLEX
        fontScale              = 1
        fontColor              = (0,255,0)
        thickness              = 1
        lineType               = 1

        # compute normalized heat map
        heatmap = cv2.normalize(self._mask_sum, None, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_GRAY2BGR)
        mask_global = cv2.cvtColor(self._mask_global, cv2.COLOR_GRAY2BGR)

        images_left = np.vstack((image, self._image_filtered[:,:,0:3]))
        images_right = np.vstack((heatmap, mask_global))
        images_4x4 = np.hstack((images_left, images_right))
        images_4x4 = cv2.resize(images_4x4, (int(2*ds*width), int(2*ds*height)))

        cv2.putText(images_4x4, 'People heatmap', (int(ds*width) + 10 , 30), font, fontScale, fontColor, thickness, lineType)
        cv2.putText(images_4x4, 'Filtered image', (10, int(ds*height) + 30 ), font, fontScale, fontColor, thickness, lineType)
        cv2.putText(images_4x4, 'Input image', (10, 30), font, fontScale, fontColor, thickness, lineType)
        cv2.putText(images_4x4, 'Global coverage', (int(ds*width) + 10, int(ds*height) + 30), font, fontScale, fontColor, thickness, lineType)

        if not self._video_out is None:
            self._video_out.write(images_4x4)

        cv2.imshow('Images', images_4x4)
        cv2.waitKey(1)

        non_zero_count = cv2.countNonZero(self._mask_global)  
        self._perc_complete = 100 * non_zero_count / (width*height)
        print(f'image {self._image_index}: remaining pixels associated with people: {100-self._perc_complete:.3f} %', end='\r')

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
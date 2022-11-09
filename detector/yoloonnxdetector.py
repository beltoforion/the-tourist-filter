import cv2
import numpy as np
from copy import deepcopy
from enum import Enum
from random import random
import argparse

from detector.detectorbase import DetectorBase

class ArgTypeMixin(Enum):

    @classmethod
    def argtype(cls, s: str) -> Enum:
        try:
            return cls[s]
        except KeyError:
            raise argparse.ArgumentTypeError(
                f"{s!r} is not a valid {cls.__name__}")

    def __str__(self):
        return self.name

class RemovalMethod(ArgTypeMixin, Enum):
    CUT = 1
    CUT_AND_MEDIAN = 2
    MEDIAN = 3
    NOISE_AND_MEDIAN = 4
    INPAINT_AND_MEDIAN = 5


# Code based on:
# https://learnopencv.com/object-detection-using-yolov5-and-opencv-dnn-in-c-and-python/#CODE-EXPLANATION-|-YOLOv5-OpenCV-DNN
class YoloOnnxDetector(DetectorBase):
    def __init__(self, method : RemovalMethod, conf_thresh : float, nms_thresh : float, score_thresh : float, box_upscale = (1.1, 1.1) ):
        super(YoloOnnxDetector, self).__init__("YoloOnnxDetector")        
        self.__method = method
        self.__box_upscale = box_upscale

        self.__net = cv2.dnn.readNet('yolov7_736x1280.onnx')
#        self.__net = cv2.dnn.readNet('yolov7-tiny_736x1280.onnx')        
        self.__net_width = 1280
        self.__net_height = 736

#        self.__net = cv2.dnn.readNet('yolov7-tiny_384x640.onnx')        
#        self.__net_width = 640
#        self.__net_height = 384

        self.__conf = conf_thresh
        self.__nms = nms_thresh
        self.__score = score_thresh

    @property
    def name_detailed(self):
        return f'yolo_{self.__method}_{self.__net_width}x{self.__net_height}_conf={self.__conf}_nms={self.__nms}_sc={self.__score}_boxus={self.__box_upscale[0]}x{self.__box_upscale[1]}'

    def __filter_detection(self, input_image, scale, output_data):
        class_ids = []
        confidences = []
        boxes = []

        rows = output_data.shape[1]

        # factors for resizing
        x_factor = 1.0/scale # image_width / self.__dim[0]
        y_factor = 1.0/scale # image_height / self.__dim[1]

        for r in range(rows):
            row = output_data[0][r]
            confidence = row[4]
            if confidence >= self.__conf:

                classes_scores = row[5:]
                _, _, _, max_indx = cv2.minMaxLoc(classes_scores)
                class_id = max_indx[1]
                if (classes_scores[class_id] > self.__score):
                    confidences.append(confidence)
                    class_ids.append(class_id)

                    x, y, w, h = row[0].item(), row[1].item(), row[2].item(), row[3].item() 
                    left = int((x - 0.5 * w) * x_factor)
                    top = int((y - 0.5 * h) * y_factor)
                    width = int(w * x_factor)
                    height = int(h * y_factor)
                    box = np.array([left, top, width, height])
                    boxes.append(box)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, self.__score, self.__nms) 

        result_class_ids = []
        result_confidences = []
        result_boxes = []

        for i in indexes:
            result_confidences.append(confidences[i])
            result_class_ids.append(class_ids[i])
            result_boxes.append(boxes[i])

        return result_class_ids, result_confidences, result_boxes


    def __preprocess_image(self, img):
        # scale the original image to fit completely into the resized image (with padding)
        height, width, _ = img.shape
        aspect = self.__net_width / self.__net_height

        if width/height >= aspect:
            scale = self.__net_width / width
        else:
            scale = self.__net_height / height

        new_width = int(scale * width)
        new_height = int(scale * height)

        # put image into a box with padding 
        img_scaled = cv2.resize(img, (new_width, new_height))
        height, width, _ = img_scaled.shape
        
        # create an image with the exact size of the detector
        img_resized = np.zeros((self.__net_height, self.__net_width, 3), np.uint8)
        height, width, _ = img_resized.shape

        img_resized[0:new_height, 0:new_width] = img_scaled
        height, width, _ = img_resized.shape
                        
        return img_resized, scale


    def restart_requested(self):
        # only the CUT_AND_MEDIA method may request a restart to clean up
        # the result. The cuts are often harsh and visible due to slight brightness
        # variations alongside the cut line
        if self.__method==RemovalMethod.CUT_AND_MEDIAN:
            self.__stack = []
            return True
        else:
            return False


    def finish_impl(self):
        if self.__method == RemovalMethod.INPAINT_AND_MEDIAN or \
           self.__method == RemovalMethod.MEDIAN or \
           self.__method == RemovalMethod.CUT_AND_MEDIAN:
            print(f'\r\nCreating median image from image stack of {len(self.__stack)} images.')
            image_stack = np.stack(self.__stack)
            composed = np.median(image_stack, axis=0).astype(dtype='uint8')
            return composed
        elif self.__method == RemovalMethod.NOISE_AND_MEDIAN:
            print(f'\r\nCreating median image from image stack of {len(self.__stack)} images.')
            
            # median requires odd numbers to work properly
            if len(self.__stack) % 2 == 0:
                self.__stack.append(self.__stack[len(self.__stack)-1])

            image_stack = np.stack(self.__stack)
            composed = np.median(image_stack, axis=0).astype(dtype='uint8')

            # residual noise needs to be inpainted
            _, mask_black = cv2.threshold(composed, 0, 1, cv2.THRESH_BINARY)
            mask_black = 255 - mask_black*255
            _, mask_white = cv2.threshold(composed, 254, 255, cv2.THRESH_BINARY)
            mask = (mask_white + mask_black)[:, :, 0]
            composed = cv2.inpaint(composed, mask, 10, cv2.INPAINT_TELEA)

            return composed
        else:
            return self._image_filtered

    def start_impl(self):
        self.__stack = []

    def next_image_impl(self, image):
        if self.__method == RemovalMethod.MEDIAN:
            self._image_filtered = image.copy()
            self.__stack.append(self._image_filtered)
        else:
            self._mask[:] = 255

            class_ids, confidences, boxes = self.detect(image)
            filtered_image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

            if self.__method == RemovalMethod.INPAINT_AND_MEDIAN:
                original_image = image.copy()
                filtered_image = image.copy()
            elif self.__method == RemovalMethod.NOISE_AND_MEDIAN:
                # Normalize image so that the darkest and brightest color is no longer used.
                # This is because the noise pattern is using both brigthness values. I will
                # remove residual noise with inpaint later. This will help filter it
                original_image = cv2.normalize(image.copy(), None, 1, 254, cv2.NORM_MINMAX)
                filtered_image = image.copy()
            else:
                filtered_image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

            for (classid, confidence, box) in zip(class_ids, confidences, boxes):
                # class id 0: People
                #       id 1: bicycle
                #       id 2: car
                #       id 3: motorcycle
                #       id 24: backpack
                #       id 25: umbrella
                #       id 26: handbag
                #       id 28: suitcase
                add_box = classid==0 or classid==1 or classid==2 or classid==3 or classid==24 or classid==25 or classid==26 or classid==28
                #add_box = True
                if add_box:
                    # the boxes are sometimes too small. I make them slightly bigger for better results
                    enlarged_box = deepcopy(box)
                    enlarged_box[2] *= self.__box_upscale[0]
                    enlarged_box[3] *= self.__box_upscale[1]

                    dx = enlarged_box[2] - box[2]
                    dy = enlarged_box[3] - box[3]

                    enlarged_box[0] -= dx / 2
                    enlarged_box[1] -= dy / 2            
                    
                    bw = enlarged_box[2]
                    bh = enlarged_box[3]

                    cv2.rectangle(self._mask, enlarged_box, 0, -1)

                    if self.__method == RemovalMethod.CUT or self.__method == RemovalMethod.CUT_AND_MEDIAN:
                        cv2.rectangle(image, enlarged_box, (0,255,0), 6)
                    elif self.__method == RemovalMethod.INPAINT_AND_MEDIAN:
                        cv2.rectangle(original_image, enlarged_box, (255,255,255), -1)
                    elif self.__method == RemovalMethod.NOISE_AND_MEDIAN:
                        # Copy binary noise into the detection box. This is done to throw off the 
                        # median filter. The noise brightness values are either 0 ore 1. When applying
                        # a median filter these values should be at the low and high end of the median 
                        # curve. (unless there are too few values)
                        noise = np.zeros((bh, bw), dtype="uint8")
                        noise = cv2.randu(noise, 0, 2) * 255
                        noise = cv2.cvtColor(noise, cv2.COLOR_GRAY2RGB)

                        if enlarged_box[0]<0:
                            enlarged_box[0] = 0
                            bw += enlarged_box[0]

                        try:
                            original_image[enlarged_box[1]:enlarged_box[1]+bh, enlarged_box[0]:enlarged_box[0]+bw, :] = noise
                        except:
                            # box is partially outside the image. I dont care...
                            pass

            # set the mask as the alpha channel of the image
            if self.__method == RemovalMethod.CUT:
                filtered_image[:, :, 3] = self._mask
                self._mask_global = cv2.bitwise_or(self._mask, self._mask_global, mask = None)
                self._add_transparent_image(self._image_filtered, filtered_image)                
                self.__stack.append(filtered_image)
            elif self.__method == RemovalMethod.CUT_AND_MEDIAN:
                filtered_image[:, :, 3] = self._mask
                self._mask_global = cv2.bitwise_or(self._mask, self._mask_global, mask = None)
                self._add_transparent_image(self._image_filtered, filtered_image)                
                self.__stack.append(self._image_filtered.copy())
            elif self.__method == RemovalMethod.NOISE_AND_MEDIAN:
                filtered_image[:, :, 0:3] = original_image
                self._image_filtered = filtered_image
                self.__stack.append(filtered_image)
            elif self.__method == RemovalMethod.INPAINT_AND_MEDIAN:
                filtered_image[:, :, 0:3] = cv2.inpaint(original_image, 255-self._mask[:], 3, cv2.INPAINT_NS)
                self._image_filtered = filtered_image
                self.__stack.append(filtered_image)

    def detect(self, img):
        img_for_yolo, scale = self.__preprocess_image(img)

        blob = cv2.dnn.blobFromImage(img_for_yolo, 1/255.0, (self.__net_width, self.__net_height), swapRB=True, crop=False)
        self.__net.setInput(blob)

        # run a forward pass to get output layers
        # the output is wrapped into a tuple, unwrap it and directly access the only element 0 
        # of the tuple
        outputs = self.__net.forward(self.__net.getUnconnectedOutLayersNames())[0]
        #print(f'{outputs[0].shape}')

        # output format:
        # X, Y, Width, Height, Confidence, Class scores of 80 Classes from the YOLO model
        class_ids, confidences, boxes = self.__filter_detection(img_for_yolo, scale, outputs)
        return class_ids, confidences, boxes

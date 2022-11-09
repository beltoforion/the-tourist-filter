import cv2
import os
import argparse
import pathlib
import glob

from detector.yoloonnxdetector import *
from detector.detectorbase import DetectorBase


def dir_or_file(path : str):
    if os.path.isdir(path) or os.path.isfile(path):
        return path
    else:
        raise NotADirectoryError(path)


def process_folder(image_folder: pathlib.Path, detector : DetectorBase):
    num_images = len(glob.glob1(str(image_folder),"*.jpg"))
    print(f'\n{detector.name}: processing folder {str(image_folder)} with {num_images} images:')

    detector.start()

    for file in image_folder.iterdir():
        if file.suffix != '.jpg':
            continue

        img = cv2.imread(str(file), cv2.IMREAD_COLOR)
        detector.next_image(img)

    if detector.restart_requested():
        for file in image_folder.iterdir():
            if file.suffix != '.jpg':
                continue

            img = cv2.imread(str(file), cv2.IMREAD_COLOR)
            detector.next_image(img)

    final_result = detector.finish()

    cv2.imwrite(f'.\{str(image_folder)}_{detector.name_detailed}.jpg', final_result)


def main():
    parser = argparse.ArgumentParser(description='The Impossible Camera - Exterminate all humans from an image stack')
    parser.add_argument("-i", "--Input", dest="input", help='The folder to run this script on', required=True, type=str)
    parser.add_argument("-m", "--Method", dest="method", type=RemovalMethod.argtype, choices=RemovalMethod, help='The method of people removal', required=True)
    parser.add_argument("-v", dest="video_file", help='Name of output video', required=False, type=str, default=None)
    args = parser.parse_args()

    print('\r\n')
    print('Exterminate all Humans (from Landscape Photos)')
    print('----------------------------------')
    print(f' - input: {args.input}')
    print(f' - method: {args.method}')    
    print(f' - output_video: {args.video_file}')    

    detector = YoloOnnxDetector(method=args.method, conf_thresh=0.01, nms_thresh=0.9, score_thresh=0.1, box_upscale=(1.05, 1.1))
    detector.video_file = args.video_file

    input = pathlib.Path(args.input)
    if not input.exists():
        print(f'The input folder or video {args.input} does not exists!')
        exit(-1)

    process_folder(pathlib.Path(args.input), detector)

if __name__ == "__main__":
    main()
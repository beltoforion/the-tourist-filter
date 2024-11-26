import os
import argparse
import pathlib

from detector.yoloonnxdetector import *
from detector.displaybase import *
from ui.ui_controller import *


def dir_or_file(path : str):
    if os.path.isdir(path) or os.path.isfile(path):
        return path
    else:
        raise NotADirectoryError(path)


def main():
    parser = argparse.ArgumentParser(description='The Tourist Filer - Exterminate all humans from an image stack')
    parser.add_argument("-n", "--hideUi", dest="hide_ui", action="store_true", help="Disable Ui")
    parser.add_argument("-i", "--Input", dest="input", help='The folder to run this script on', required=False, type=str)
    parser.add_argument("-m", "--Method", dest="method", type=RemovalMethod.argtype, choices=RemovalMethod, help='The method of people removal', required=False, default=RemovalMethod.INPAINT_AND_MEDIAN)
    parser.add_argument("-v", dest="video_file", help='Name of output video', required=False, type=str, default=None)
    args = parser.parse_args()

    detector = YoloOnnxDetector(method=args.method, conf_thresh=0.01, nms_thresh=0.9, score_thresh=0.1, box_upscale=(1.05, 1.1))
    detector.video_file = args.video_file

    if args.input is None:
        ui = UiController(detector)
        ui.show()
    else:
        print('\r\n')
        print('Exterminate all Humans (from Landscape Photos)')
        print('----------------------------------')
        print(f' - input: {args.input}')
        print(f' - method: {args.method}')    
        print(f' - output_video: {args.video_file}')    
        print(f' - hide ui: {args.hide_ui}')    

        if args.hide_ui:
            detector.setDisplay(NullDisplay())
        else:
            detector.setDisplay(OpenCvDisplay())

        input = pathlib.Path(args.input)
        if not input.exists():
            print(f'The input folder or video {args.input} does not exists!')
            exit(-1)

        detector.process_folder(pathlib.Path(args.input))


if __name__ == "__main__":
    main()
   
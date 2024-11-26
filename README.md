[![GitHub issues](https://img.shields.io/github/issues/beltoforion/the-tourist-filter.svg?maxAge=360)](https://github.com/beltoforion/the-tourist-filter/issues)
![titel-touristenfilter](https://user-images.githubusercontent.com/2202567/201741382-95196fa1-45ee-40a6-9748-07e513c77d85.jpg)

# The Tourist Filter

## Removing People from images

This app was created to allow nature photography in crowded tourist spots via improved median stacking methods. I wrote it because I made a couple of image stacks during a trip to Island and discovered that median stacking of the images in Photoshop does not produce satisfying results out of the box. The improved median stacking algorithms implemented here will work much better. The basic idea is to combine an object detector like YOLOv7 and preprocess the images in a way that will make median stacking more likely to succeed.

For this purpose i implemented several methods of preprocessing the stack with the help of the YOLOv7 object detector trained on the COCO dataset. 

![link_cut](https://user-images.githubusercontent.com/2202567/201495454-81ced94b-84b1-462d-9614-6beb505a72e1.jpg)

You can find more details on the accompanying web page:
* english: https://beltoforion.de/en/the-tourist-filter
* german:  https://beltoforion.de/de/touristenfilter

## Input images 

To use this script you need a stack of images either taken on a tripod or aligned by other means. The images should be taken a couple of seconds apart
and you should have enough images so that every part of the scene is free of peopla in at least one image.

![screenshot](https://user-images.githubusercontent.com/2202567/228079613-8cb2c70c-6b01-4260-9095-a833d162933a.jpg)

## Usage

You need python to execute this script. Put your images into a folder and then run the script on the content of this folder.

```python
python ./filter-all-tourists.py -i ./stack1 -m CUT
```

## Command Line Options

<b>-i</b><br/> Path to the input folder. Folder must contain a series of images which are alsready properly aligned. Either taken with a tripod or aligned by other means.
<br/><br/>
<b>-m</b><br/> Select the method to use. Options are CUT, CUT_AND_MEDIAN, MEDIAN, NOISE_AND_MEDIAN, INPAINT_AND_MEDIAN
<br/><br/>
<b>-v</b><br/> Name of a video file for debug purposes.
<br/><br/>
<b>-n</b><br/> Disable output window.

## Example

An image stack being processed with an algoithm that is usung YOLOv7 for people detection and is covering all detected people with binary noise.

[video_stack3_noise.webm](https://user-images.githubusercontent.com/2202567/201500754-80de06ca-9552-45a1-b1d6-4a4ec500ba29.webm)

The resulting median stack of the processed series is shown here:

![stack3_yolo_NOISE_AND_MEDIAN](https://user-images.githubusercontent.com/2202567/201500837-9a376880-a956-4d6d-8eae-61b465a6e735.jpg)

<!--
[video_stack5_cut.webm](https://user-images.githubusercontent.com/2202567/201433129-b832e448-03a4-4c5b-b831-2430dee2d31a.webm)
-->

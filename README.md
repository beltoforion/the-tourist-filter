# The Tourist Filter

This skript was created to allow nature photography in crowded tourist spots via improved median stacking methods. I wrote it because I made a couple of image stacks during a trip to Island and discovered that median stacking of the images in Photoshop does not produce satisfying results out of the box. The improved median stacking algorithms implemented here will work much better! The basic idea is to combine an object detector like YOLOv7 and preprocess the images in a way that will make median stacking more likely to succeed.

For this purpose i implemented several methods of preprocessing the stack with the help of the YOLOv7 object detector trained on the COCO dataset. 

![link_cut](https://user-images.githubusercontent.com/2202567/201495454-81ced94b-84b1-462d-9614-6beb505a72e1.jpg)

You can find more details on the accomanying (german) web page:
https://beltoforion.de/de/touristenfilter/
(Non-German Readers: Please try the chrome browser as it provides a fairly decend automatic translation of the page. I will probably create a translation if there is sufficient interest in the topic)

## Input images 

To use this script you need a stack of images either taken on a tripod or aligned by other means. The images should be taken a couple of seconds apart
and you should have enough images so that every part of the scene is free of peopla in at least one image.

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

## Example

An image stack being processed with an algoithm that is usung YOLOv7 for people detection and is covering all detected people with binary noise.

[video_stack3_noise.webm](https://user-images.githubusercontent.com/2202567/201500754-80de06ca-9552-45a1-b1d6-4a4ec500ba29.webm)

The resulting median stack of the processed series is shown here:

![stack3_yolo_NOISE_AND_MEDIAN](https://user-images.githubusercontent.com/2202567/201500837-9a376880-a956-4d6d-8eae-61b465a6e735.jpg)

<!--
[video_stack5_cut.webm](https://user-images.githubusercontent.com/2202567/201433129-b832e448-03a4-4c5b-b831-2430dee2d31a.webm)
-->

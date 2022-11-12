# The Tourist Filter

This skript was created to allow nature photography in crowded tourist spots via improved median stacking methods. I wrote it because I made a couple of image stacks during a trip to Island and discovered that median stacking of the images in Photoshop does not produce satisfying results out of the box. The improved median stacking algorithms implemented here will work much better! The basic idea is to combine an object detector like YOLOv7 and preprocess the images in a way that will make median stacking more likely to succeed.

For this purpose i implemented several methods of preprocessing the stack with the help of the YOLOv7 object detector trained on the COCO dataset. 

![link_cut](https://user-images.githubusercontent.com/2202567/201495454-81ced94b-84b1-462d-9614-6beb505a72e1.jpg)

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

[video_stack5_cut.webm](https://user-images.githubusercontent.com/2202567/201433129-b832e448-03a4-4c5b-b831-2430dee2d31a.webm)

# The Tourist Filter

A collection of different algorithms to remove people from Stacks of images to fully automatically create images without any People. It works better
than ordinary Median-Stacking and is capable of removing Tourists without much remainging artifacts.

## Input images 

To use this script you need a stack of images either taken on a tripod or aligned by other means. The images should be taken a couple of seconds apart
and you should have enough images so that every part of the scene is free of peopla in at least one image.

## Usage

You need python to execute this script. Put your images into a folder and then run the script on the content of this folder.

```python
python ./filter-all-tourists.py -i ./stack1 -m CUT
```

## Command Line Options

-i<br/> Path to the input folder. Folder must contain a series of images which are alsready properly aligned. Either taken with a tripod or aligned by other means.
<br/><br/>
-m<br/> Select the method to use. Options are CUT, CUT_AND_MEDIAN, MEDIAN, NOISE_AND_MEDIAN, INPAINT_AND_MEDIAN

[video_stack5_cut.webm](https://user-images.githubusercontent.com/2202567/201433129-b832e448-03a4-4c5b-b831-2430dee2d31a.webm)

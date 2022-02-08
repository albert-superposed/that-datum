# that-datum
Repo of tools for you to struggle lazily with data preparation.<br>
Built with Python Tkinter. (Theme used - Azure https://github.com/rdbende/Azure-ttk-theme)<br>

![Yes](https://github.com/u-need-dropout/that-datum/blob/main/images/violet-hai.gif)

Current applications:<br>
+ Peel<br>
+ AnoDatum<br>

----

## Peel
Peel helps you to transform video into image frames.<br>

    python -m Peel

![Demo](https://github.com/u-need-dropout/that-datum/blob/main/images/Peel-demo.png)

Supported file foramts:<br>
+ avi<br>
+ mp4<br>

----

## Anota
Anota is a tool design for annotating image data.<br>

    python -m Anota

![Demo1](https://github.com/u-need-dropout/that-datum/blob/main/images/Anota-demo.png)

![Demo2](https://github.com/u-need-dropout/that-datum/blob/main/images/Anota-demo-dark.png)

![Demo3](https://github.com/u-need-dropout/that-datum/blob/main/images/Anota-demo.gif)

Supports 'loading and saving settings'.<br>
Compatible with any aspect ratios.<br>

Supported annotating schemes:<br>
+ Classic (one label at a time) <br>
+ Extended (multiple labels at a time) <br>
+ Hierarchical (multilabels with relation and controlled selection at a time) <br>

Current supported annotating modes:<br>
+ Bounding Box (format - [labelid, centre_x, centre_y, width, height])<br>
+ Landmark (format - [landmarkid, x, y])<br>

**Note: Everything is now Relational and in the range [0, 1] <br>
rounded to 4 decimals to be consistent with various aspect ratios.**<br>

Supported file formats:<br>
+ png<br>
+ jpg

### Usage
#### Bounding Box
1. Left click to start drawing.
2. Freely hover over the image.
3. Get help from Ctrl to force shape the box square.
4. Click again to finalise the box.

#### Landmark
1. Left click to mark the landmark.

*Dont't forget to click 'save' to save your work.*

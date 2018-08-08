
# python-showcase


* Sergio Perea, (c) 2018
* Dev/Source: https://github.com/sperea/python-escaparate
* License: GNU GPLv3


python-showcase is an automatic playback image viewer developed with Python3 + Tk.

This script is very useful to play looping slideshows on a TV with a RaspberryPi connected. 

We can control the display time between photos.

**Example**

    $ ./python-escaparate.py -s -t 10000 /home/sergio/images

**Requirements**:

* Python 3.6+
* Tkinter (python-tk, python-imaging-tk)
* Pillow (python-imaging)

install requirements on Debian/Ubuntu::

    $ sudo apt-get install python-tk python-imaging-tk

install PIL/Pillow as a system package on Debian/Ubuntu::

    $ sudo apt-get install python-imaging

or, install PIL/Pillow from PyPI::

    $ sudo apt-get build-dep pillow
    $ sudo pip install pillow

**Command Line Help**::

    $ easymiv.py -h
    usage: easymiv.py [-h] [-s] [-r] dir

    positional arguments:
      dir              directory of images

    optional arguments:
      -h, --help       show this help message and exit
      -s, --slideshow  slideshow mode
      -t, --time     time between photos
      

**Keyboard Controls**:

**Quit:**
* q
* escape
* control-c

**Show Next:**
* space
* right
* down
* return

**Show Previous:**
* left
* up

----

python-escaparate was originally forked from: https://github.com/cgoldberg/easymiv




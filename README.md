
# python-escaparate


* Sergio Perea, (c) 2018
* A partir de un fork de un programa de Corey Goldberg, (c) 2013, 2015
* Dev/Source: https://github.com/sperea/easymiv
* License: GNU GPLv3


python-escaparate  is an automatic playback image viewer developed with Python + Tk
This script is very useful to use in a RaspberryPi connected to the TV of a showcase.
We can control the display time between photos.


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

* Quit:
 * q
 * <escape>
 * <control>-c

* Show Next:
 * <space>
 * <right>
 * <down>
 * <return>

* Show Previous:
 * <left>
 * <up>

----

EasyMIV was originally forked from: Miv (Minimal Image Viewer) 0.0.2, (c) 2012 madebits


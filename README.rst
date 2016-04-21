===================================
easymiv - easy minimal image viewer
===================================

* Corey Goldberg, (c) 2013, 2015
* Dev/Source: https://github.com/cgoldberg/easymiv
* License: GNU GPLv3

-------------------------------------
full-screen image slideshow in Python
-------------------------------------

**Requirements**:

* Python 2.7+ or 3.3+
* Tkinter (python-tk, python-imaging-tk)
* PIL/Pillow (python-imaging)

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
      -r, --random     random shuffle images

**Example**::

    $ git clone https://github.com/cgoldberg/easymiv.git
    $ cd easymiv
    $ easymiv.py /home/cgoldberg/images/

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


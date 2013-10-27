#!/usr/bin/env python
#
#  EasyMiv - a fork of Miv
#  Corey Goldberg, (c) 2013, (http://goldb.org)
#  License: GNU GPLv3
#
#  original was based on code from: Miv - Minimal Image Viewer, version 0.0.2
#  (c) 2012, http://madebits.com
#
#  Requirements:
#   * Python 2.7+ or 3.2+
#   * python-imaging-tk


import argparse
import os
import re
import sys

try:
    from Tkinter import *  # Python 2
except ImportError:
    from tkinter import *  # Python 3

from PIL import Image
from PIL.ImageTk import PhotoImage


class Config:
    def __init__(self):
        self.detectImages = True
        self.loop = True
        self.autoSlideTime = 3000
        self.autoSlideAutoStart = False
        
# http://code.activestate.com/recipes/135435-sort-a-string-using-numeric-order/
def stringSplitByNumbers(x):
    r = re.compile('(\d+)')
    l = r.split(x.lower())
    return [toNumber(y) if y.isdigit() else y for y in l]

def toNumber(y):
    try:
        return int(y)
    except:
        return long(y) # Python 2

class SlideShow:
    def __init__(self, inputPath):
        self.currentIndex = -1;
        self.startCurrentIndex = -1;
        self.inputPath = inputPath
        self.inputDir = self.inputPath
        inputFile = None
        if os.path.isfile(self.inputPath):
            self.inputDir,inputFile = os.path.split(self.inputPath)
        self.currentIndex = 0
        allData = os.listdir(self.inputDir)
        if (allData == None) or (len(allData) <= 0):
            return;
        allData = sorted(allData, key=stringSplitByNumbers)
        self.files = []
        for f in allData:
            tf = os.path.join(self.inputDir, f)
            if os.path.isfile(tf):
                canAdd = True
                if config.detectImages:
                    try:
                        timg = Image.open(tf)
                    except:
                        canAdd = False
                if not canAdd:
                    continue
                self.files.append(tf)
                if((inputFile != None) and (inputFile == f)):
                    self.currentIndex = len(self.files) - 1
        self.startCurrentIndex = self.currentIndex

    def hasFiles(self):
        return (self.files != None) and (len(self.files) > 0)

    def getCurrent(self):
        if not self.hasFiles():
            raise StopIteration
        return self.files[self.currentIndex]

    def getExtra(self):
        return '[%d / %d]  ' % (self.currentIndex + 1, len(self.files))

    def moveNext(self):
        if not self.hasFiles():
            raise StopIteration
        self.currentIndex += 1
        if self.currentIndex >= len(self.files):
            self.currentIndex = 0;
        if (not config.loop) and (self.startCurrentIndex == self.currentIndex):
            raise StopIteration
        return self.getCurrent()

    def movePrevious(self):
        if not self.hasFiles():
            raise StopIteration
        self.currentIndex -= 1
        if self.currentIndex < 0:
            self.currentIndex = len(self.files) - 1
        if (not config.loop) and (self.startCurrentIndex == self.currentIndex):
            raise StopIteration
        return self.getCurrent()
        
    def moveFirst(self, first):
        if not self.hasFiles():
            raise StopIteration
        self.currentIndex = 0
        if not first:
            self.currentIndex = len(self.files) - 1
        return self.getCurrent()

class Display:
    def __init__(self, root):
        self.root = root
        self.masterimage = None
        self.photoimage = None
        self.imageId = -1
        self.textId = -1
        self.currentFile = None
        self.display = Canvas(root, bg='black', borderwidth=0, highlightthickness=0)
        self.display.pack(expand=YES, fill=BOTH)

    def hasValidImage(self):
        return (self.photoimage is not None)

    def _zoomImage(self, img, w, h):
        originalWidth = img.size[0]
        r = min(float(w) / img.size[0], float(h) / img.size[1])
        img = img.resize((int(img.size[0] * r), int(img.size[1] * r)), Image.BILINEAR)
        currentZoom = int((float(img.size[0]) / originalWidth) * 100);
        text = '%s%%' % currentZoom
        return img, text

    def setImage(self, file, extra, reloadImage=True):
        self.photoimage = None
        self.masterimage = None
        if file == None:
            return
        self.currentFile = file
        text = os.path.basename(file)
        text = extra + text
        if (self.masterimage == None) or reloadImage:
            self.masterimage = Image.open(file)
        w, h = self.display.winfo_width(), self.display.winfo_height()
        img, zoomText = self._zoomImage(self.masterimage, w, h)
        size = '%sx%s' % self.masterimage.size
        text += '  [%s]  %s' % (size, zoomText)
        self.photoimage = PhotoImage(img)
        if self.imageId < 0:
            self.imageId = self.display.create_image(0, 0)
        self.display.coords(self.imageId, w // 2, h // 2)
        self.display.itemconfig(self.imageId, image=self.photoimage, anchor=CENTER)
        self.hasImage = True

        # set text
        if self.textId < 0:
            self.textId = self.display.create_text(5, 5)
        self.display.itemconfig(self.textId, text=text, anchor=NW, fill='red')
        self.display.lift(self.textId)

    
class Application:
    def __init__(self, root):
        self.autoSlideOn = False
        self.mstart = (-1, -1)
        self.slide = None
        self.root = root
        self.root.config(borderwidth=0, cursor='none')
        self.display = Display(root)
        self.root.bind('q', quit)
        self.root.bind('<Escape>', quit)
        self.root.bind('<Control-c>', quit)
        self.root.bind('<space>', lambda e:  self.showNext(e, True))
        self.root.bind('<Right>', lambda e: self.showNext(e, True))
        self.root.bind('<Down>', lambda e: self.showNext(e, True))
        self.root.bind('<Return>', lambda e: self.showNext(e, True))
        self.root.bind('<Left>', lambda e: self.showNext(e, False))
        self.root.bind('<Up>', lambda e: self.showNext(e, False))
        self.root.bind('s', lambda e: self.autoSlide())
        # bind function keys F1-F12
        for i in range(12):
            funtion_key_label = '<F%d>' % (i +1)
            self.root.bind(funtion_key_label, lambda e: self.autoSlide())
        

    def run(self, inputPath):
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry('%dx%d+0+0' % (w, h))
        self.root.attributes('-fullscreen', True)

        self.inputPath = inputPath
        self._initFiles(inputPath)
        self.root.focus_set()
        self.root.focus_force()
        self.root.mainloop()

    def _initFiles(self, inputPath):
        self.slide = SlideShow(inputPath)
        self.root.after(150, lambda: self.showCurrent())

    def showNext(self, e, down):
        if self.slide is None:
            return
        try:
            if down:
                self.slide.moveNext()
            else:
                self.slide.movePrevious()
            self.showCurrent()
        except StopIteration:
            quit(e)

    def showCurrent(self):
        global config
        if self.slide is None:
            return
        self.display.setImage(self.slide.getCurrent(), self.slide.getExtra(), True)
        if config.autoSlideAutoStart:
            config.autoSlideAutoStart = False
            self.root.after(config.autoSlideTime, lambda: self.autoSlide())

    def autoSlide(self):
        self.autoSlideOn = True
        self.showNext(None, True)
        self.root.after(config.autoSlideTime, lambda: self.autoSlideNext())

    def autoSlideNext(self):
        self.showNext(None, True)
        self.root.after(config.autoSlideTime, lambda: self.autoSlideNext())

    def autoSlideStop(self):
        self.autoSlideOn = False


def quit(e):
    root.destroy()

if __name__ == '__main__':
    global config
    root = Tk()
    config = Config()
    parser = argparse.ArgumentParser()
    parser.add_argument('dir')
    parser.add_argument('-s', '--slideshow', help='start slideshow', action='store_true')
    args = parser.parse_args()
    if args.slideshow:
        config.autoSlideAutoStart = True
    app = Application(root)
    app.run(args.dir)

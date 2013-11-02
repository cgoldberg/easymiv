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
import random
import os

try:
    from Tkinter import *  # Python 2
except ImportError:
    from tkinter import *  # Python 3

from PIL import Image
from PIL.ImageTk import PhotoImage


class SlideShow:

    def __init__(self, input_dir, randomize=True):
        self.current_index = 0
        img_paths = []
        for root, dirs, files in os.walk(input_dir, topdown=True):
            for file in sorted(files):
                path = os.path.abspath(os.path.join(root, file))
                try:
                    Image.open(path)
                    img_paths.append(path)
                except IOError:
                    pass
        if not img_paths:
            print 'no images found'
            sys.exit()
        if randomize:
            random.shuffle(img_paths)
        self.files = img_paths

    def get_current(self):
        return self.files[self.current_index]

    def get_extra(self):
        return '%d / %d' % (self.current_index + 1, len(self.files))

    def move_next(self):
        self.current_index += 1
        if self.current_index >= len(self.files):
            self.current_index = 0
        return self.get_current()

    def move_previous(self):
        self.current_index -= 1
        if self.current_index < 0:
            self.current_index = len(self.files) - 1
        return self.get_current()


class Display:

    def __init__(self, root):
        self.root = root
        self.image_id = None
        self.text_id = None
        self.display = Canvas(
            root, bg='black', borderwidth=0, highlightthickness=0)
        self.display.pack(expand=YES, fill=BOTH)

    def _zoom_image(self, img, w, h):
        original_width = img.size[0]
        r = min(float(w) / img.size[0], float(h) / img.size[1])
        img = img.resize(
            (int(img.size[0] * r), int(img.size[1] * r)), Image.BILINEAR)
        current_zoom = int((float(img.size[0]) / original_width) * 100)
        zoom_text = '%s%%' % current_zoom
        return img, zoom_text

    def set_image(self, file, extra):
        self.current_file = file
        w = self.display.winfo_width()
        h = self.display.winfo_height()
        self.masterimage = Image.open(file)
        img, zoom_text = self._zoom_image(self.masterimage, w, h)
        self.photoimage = PhotoImage(img)
        size = '%sx%s' % self.masterimage.size
        text = '[%s]  %s  (%s)  %s' % (
            extra, os.path.basename(file), size, zoom_text)

        if self.image_id is None:
            self.image_id = self.display.create_image(0, 0)
        self.display.coords(self.image_id, w // 2, h // 2)
        self.display.itemconfig(
            self.image_id, image=self.photoimage, anchor=CENTER)

        # set text
        if self.text_id is None:
            self.text_id = self.display.create_text(5, 5)
        self.display.itemconfig(self.text_id, text=text, anchor=NW, fill='red')
        self.display.lift(self.text_id)


class Application:

    def __init__(self, root, auto_slide_on=False, auto_slide_time=3000):
        self.root = root
        self.auto_slide_on = auto_slide_on
        self.auto_slide_time = auto_slide_time
        self.root.config(borderwidth=0, cursor='none')
        self.root.bind('q', lambda e: self.quit())
        self.root.bind('<Escape>', lambda e: self.quit())
        self.root.bind('<Control-c>', lambda e: self.quit())
        if not self.auto_slide_on:
            self.root.bind('<Right>', lambda e: self.show_next())
            self.root.bind('<Down>', lambda e: self.show_next())
            self.root.bind('<Left>', lambda e: self.show_next(False))
            self.root.bind('<Up>', lambda e: self.show_next(False))
            self.root.bind('<Return>', lambda e: self.show_next())
            self.root.bind('<space>', lambda e: self.show_next())
        self.display = Display(self.root)

    def run(self, input_dir, randomize=True):
        if not os.path.isdir(input_dir):
            sys.stderr.write('%r is not a directory\n' % input_dir)
            sys.exit(1)
            
        
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        self.root.geometry('%dx%d+0+0' % (w, h))
        self.root.attributes('-fullscreen', True)

        self.slides = SlideShow(input_dir, randomize)
        self.root.after(150, lambda: self.show_current())

        self.root.focus_set()
        self.root.focus_force()
        self.root.mainloop()

    def show_next(self, forward=True):
        if forward:
            self.slides.move_next()
        else:
            self.slides.move_previous()
        self.show_current()

    def show_current(self):
        self.display.set_image(
            self.slides.get_current(), self.slides.get_extra())
        if self.auto_slide_on:
            self.root.after(self.auto_slide_time, lambda: self.auto_slide())

    def auto_slide(self):
        self.show_next()
        self.root.after(self.auto_slide_time, lambda: self.auto_slide())

    def quit(self):
        self.root.destroy()


if __name__ == '__main__':
    root = Tk()
    parser = argparse.ArgumentParser()
    parser.add_argument('dir')
    parser.add_argument(
        '-s', '--slideshow', help='start slideshow', action='store_true')
    parser.add_argument(
        '-r', '--random', help='random shuffle images', action='store_true')
    args = parser.parse_args()
    app = Application(root, args.slideshow, 3000)
    app.run(args.dir, args.random)

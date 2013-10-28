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


try:
    from Tkinter import *  # Python 2
except ImportError:
    from tkinter import *  # Python 3

from PIL import Image
from PIL.ImageTk import PhotoImage


class Config:

    def __init__(self):
        self.detect_images = True
        self.auto_slide_time = 3000
        self.auto_slide_auto_start = False


class SlideShow:
    def __init__(self, input_path):
        self.current_index = -1
        self.startcurrent_index = -1
        self.input_path = input_path
        self.input_dir = self.input_path
        input_file = None
        if os.path.isfile(self.input_path):
            self.input_dir, input_file = os.path.split(self.input_path)
        self.current_index = 0
        all_data = sorted(os.listdir(self.input_dir))
        if ((all_data is None) or (len(all_data) <= 0)):
            return
        self.files = []
        for f in all_data:
            tf = os.path.join(self.input_dir, f)
            if os.path.isfile(tf):
                can_add = True
                if config.detect_images:
                    try:
                        Image.open(tf)
                    except Exception:
                        can_add = False
                if not can_add:
                    continue
                self.files.append(tf)
                if ((input_file is not None) and (input_file == f)):
                    self.current_index = len(self.files) - 1
        self.startcurrent_index = self.current_index

    def has_files(self):
        return ((self.files is not None) and (len(self.files) > 0))

    def get_current(self):
        if not self.has_files():
            raise StopIteration
        return self.files[self.current_index]

    def get_extra(self):
        return '[%d / %d]  ' % (self.current_index + 1, len(self.files))

    def move_next(self):
        if not self.has_files():
            raise StopIteration
        self.current_index += 1
        if self.current_index >= len(self.files):
            self.current_index = 0
        return self.get_current()

    def move_previous(self):
        if not self.has_files():
            raise StopIteration
        self.current_index -= 1
        if self.current_index < 0:
            self.current_index = len(self.files) - 1
        return self.get_current()

    def move_first(self, first):
        if not self.has_files():
            raise StopIteration
        self.current_index = 0
        if not first:
            self.current_index = len(self.files) - 1
        return self.get_current()


class Display:
    def __init__(self, root):
        self.root = root
        self.masterimage = None
        self.photoimage = None
        self.image_id = -1
        self.text_id = -1
        self.currentFile = None
        self.display = Canvas(
            root, bg='black', borderwidth=0, highlightthickness=0)
        self.display.pack(expand=YES, fill=BOTH)

    def has_valid_image(self):
        return (self.photoimage is not None)

    def _zoom_image(self, img, w, h):
        original_width = img.size[0]
        r = min(float(w) / img.size[0], float(h) / img.size[1])
        img = img.resize(
            (int(img.size[0] * r), int(img.size[1] * r)), Image.BILINEAR)
        current_zoom = int((float(img.size[0]) / original_width) * 100)
        text = '%s%%' % current_zoom
        return img, text

    def set_image(self, file, extra, reload_image=True):
        self.photoimage = None
        self.masterimage = None
        if file is None:
            return
        self.currentFile = file
        text = os.path.basename(file)
        text = extra + text
        if ((self.masterimage is None) or reload_image):
            self.masterimage = Image.open(file)
        w, h = self.display.winfo_width(), self.display.winfo_height()
        img, zoomText = self._zoom_image(self.masterimage, w, h)
        size = '%sx%s' % self.masterimage.size
        text += '  [%s]  %s' % (size, zoomText)
        self.photoimage = PhotoImage(img)
        if self.image_id < 0:
            self.image_id = self.display.create_image(0, 0)
        self.display.coords(self.image_id, w // 2, h // 2)
        self.display.itemconfig(
            self.image_id, image=self.photoimage, anchor=CENTER)
        self.hasImage = True

        # set text
        if self.text_id < 0:
            self.text_id = self.display.create_text(5, 5)
        self.display.itemconfig(self.text_id, text=text, anchor=NW, fill='red')
        self.display.lift(self.text_id)


class Application:

    def __init__(self, root):
        self.auto_slide_on = False
        self.mstart = (-1, -1)
        self.slide = None
        self.root = root
        self.root.config(borderwidth=0, cursor='none')
        self.display = Display(root)
        self.root.bind('q', quit)
        self.root.bind('<Escape>', quit)
        self.root.bind('<Control-c>', quit)
        self.root.bind('<space>', lambda e: self.show_next(e, True))
        self.root.bind('<Right>', lambda e: self.show_next(e, True))
        self.root.bind('<Down>', lambda e: self.show_next(e, True))
        self.root.bind('<Return>', lambda e: self.show_next(e, True))
        self.root.bind('<Left>', lambda e: self.show_next(e, False))
        self.root.bind('<Up>', lambda e: self.show_next(e, False))
        self.root.bind('s', lambda e: self.auto_slide())
        # bind function keys: F1-F12
        for i in range(12):
            funtion_key_label = '<F%d>' % (i + 1)
            self.root.bind(funtion_key_label, lambda e: self.auto_slide())

    def run(self, input_path):
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry('%dx%d+0+0' % (w, h))
        self.root.attributes('-fullscreen', True)

        self.input_path = input_path
        self._init_files(input_path)
        self.root.focus_set()
        self.root.focus_force()
        self.root.mainloop()

    def _init_files(self, input_path):
        self.slide = SlideShow(input_path)
        self.root.after(150, lambda: self.show_current())

    def show_next(self, e, down):
        if self.slide is None:
            return
        try:
            if down:
                self.slide.move_next()
            else:
                self.slide.move_previous()
            self.show_current()
        except StopIteration:
            quit(e)

    def show_current(self):
        global config
        if self.slide is None:
            return
        self.display.set_image(
            self.slide.get_current(), self.slide.get_extra(), True)
        if config.auto_slide_auto_start:
            config.auto_slide_auto_start = False
            self.root.after(config.auto_slide_time, lambda: self.auto_slide())

    def auto_slide(self):
        self.auto_slide_on = True
        self.show_next(None, True)
        self.root.after(config.auto_slide_time, lambda: self.auto_slide_next())

    def auto_slide_next(self):
        self.show_next(None, True)
        self.root.after(config.auto_slide_time, lambda: self.auto_slide_next())

    def auto_slide_stop(self):
        self.auto_slide_on = False


def quit(e):
    root.destroy()

if __name__ == '__main__':
    global config
    root = Tk()
    config = Config()
    parser = argparse.ArgumentParser()
    parser.add_argument('dir')
    parser.add_argument(
        '-s', '--slideshow', help='start slideshow', action='store_true')
    args = parser.parse_args()
    if args.slideshow:
        config.auto_slide_auto_start = True
    app = Application(root)
    app.run(args.dir)

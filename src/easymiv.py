# Copyright (c) 2013-2026 Corey Goldberg
# SPDX-License-Identifier: GPL-3.0-only
#
#  EasyMIV - Easy minimal image viewer (full-screen image slideshow)


import argparse
import random
import sys
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageOps
from PIL.ImageTk import PhotoImage


class SlideShow:
    def __init__(self, input_dir, randomize=True):
        self.current_index = 0
        self.files = sorted(
            path.resolve()
            for path in Path(input_dir).rglob("*")
            if path.is_file() and self.is_valid_image(path)
        )
        if not self.files:
            msg = f"No images found in {input_dir}"
            raise ValueError(msg)
        if randomize:
            random.shuffle(self.files)

    @staticmethod
    def is_valid_image(path):
        try:
            with Image.open(path) as image:
                image.verify()
        except (OSError, SyntaxError, ValueError):
            return False
        else:
            return True

    def get_current(self):
        return self.files[self.current_index]

    def get_extra(self):
        return f"{self.current_index + 1} / {len(self.files)}"

    def move_next(self):
        self.current_index = (self.current_index + 1) % len(self.files)
        return self.get_current()

    def move_previous(self):
        self.current_index = (self.current_index - 1) % len(self.files)
        return self.get_current()


class Display:
    def __init__(self, root):
        self.root = root
        self.image_id = None
        self.text_id = None
        self.display = tk.Canvas(
            root,
            bg="black",
            borderwidth=0,
            highlightthickness=0,
        )
        self.display.pack(expand=tk.YES, fill=tk.BOTH)

    def _zoom_image(self, img, width, height):
        if width <= 0 or height <= 0:
            return img.copy(), "100%"
        original_width = img.width
        scale = min(width / img.width, height / img.height)
        img = img.resize(
            (max(1, int(img.width * scale)), max(1, int(img.height * scale))),
            Image.Resampling.LANCZOS,
        )
        zoom_text = f"{int(img.width / original_width * 100)}%"
        return img, zoom_text

    def set_image(self, file, extra):
        width = self.display.winfo_width()
        height = self.display.winfo_height()
        with Image.open(file) as image:
            masterimage = ImageOps.exif_transpose(image).copy()
        img, zoom_text = self._zoom_image(masterimage, width, height)
        self.photoimage = PhotoImage(img)
        img_width, img_height = masterimage.size
        size = f"{img_width}x{img_height}"
        text = f"[{extra}]  {Path(file).name}  ({size})  {zoom_text}"
        if self.image_id is None:
            self.image_id = self.display.create_image(0, 0)
        self.display.coords(self.image_id, width // 2, height // 2)
        self.display.itemconfig(
            self.image_id,
            image=self.photoimage,
            anchor=tk.CENTER,
        )
        # set text
        if self.text_id is None:
            self.text_id = self.display.create_text(5, 5)
        self.display.itemconfig(self.text_id, text=text, anchor=tk.NW, fill="red")
        self.display.lift(self.text_id)


class Application:
    def __init__(self, root, auto_slide_on=False, auto_slide_time=3000):
        self.root = root
        self.auto_slide_on = auto_slide_on
        self.auto_slide_time = auto_slide_time
        self.root.config(borderwidth=0, cursor="none")
        self.root.bind("q", lambda _: self.quit())
        self.root.bind("<Escape>", lambda _: self.quit())
        self.root.bind("<Control-c>", lambda _: self.quit())
        if not self.auto_slide_on:
            self.root.bind("<Right>", lambda _: self.show_next())
            self.root.bind("<Down>", lambda _: self.show_next())
            self.root.bind("<Left>", lambda _: self.show_next(False))
            self.root.bind("<Up>", lambda _: self.show_next(False))
            self.root.bind("<Return>", lambda _: self.show_next())
            self.root.bind("<space>", lambda _: self.show_next())
        self.display = Display(self.root)
        self._slide_after_id = None

    def run(self, input_dir, randomize=True):
        input_dir = Path(input_dir)
        if not input_dir.is_dir():
            raise NotADirectoryError(input_dir)
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.root.geometry(f"{width}x{height}+0+0")
        self.root.attributes("-fullscreen", True)
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
            self.slides.get_current(),
            self.slides.get_extra(),
        )

        if self.auto_slide_on:
            if self._slide_after_id is not None:
                self.root.after_cancel(self._slide_after_id)

            self._slide_after_id = self.root.after(
                self.auto_slide_time,
                self.auto_slide,
            )

    def auto_slide(self):
        self._slide_after_id = None
        self.show_next()

    def quit(self):
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "dir",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="directory of images (scans recursively)",
    )
    parser.add_argument(
        "-s",
        "--slideshow",
        action="store_true",
        help="slideshow mode",
    )
    parser.add_argument(
        "-r",
        "--random",
        action="store_true",
        help="randomly shuffle images",
    )
    args = parser.parse_args()

    if not args.dir.is_dir():
        sys.exit(f"not a directory: {args.dir}")

    root = tk.Tk()
    try:
        app = Application(root, args.slideshow, 3000)
        app.run(args.dir, args.random)
    except ValueError as e:
        root.destroy()
        sys.exit(e)
    except KeyboardInterrupt:
        root.destroy()


if __name__ == "__main__":
    main()

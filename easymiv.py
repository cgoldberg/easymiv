#!/usr/bin/env python

# Minimal image viewer
# (C) 2012 http://madebits.com
# No warranty. Use as it fits to you.

import os, sys
import re
import subprocess

try:
    from Tkinter import *
    from tkMessageBox import *
    from tkFileDialog import *
    import urllib2
    
except:
    from tkinter import *
    from tkinter.messagebox import *
    from tkinter.filedialog import *
    import urllib

from PIL import Image
from PIL.ImageTk import PhotoImage

# code

class Config:
    def __init__(self):
        self.fullScreen = True
        self.detectImages = False
        self.autoSlideTime = 3000
        self.autoSlideAutoStart = False
        self.loop = True
        self.defaultZoom = -3
        
root = Tk()
config = Config()

# http://code.activestate.com/recipes/135435-sort-a-string-using-numeric-order/
def stringSplitByNumbers(x):
    r = re.compile('(\d+)')
    l = r.split(x.lower())
    return [toNumber(y) if y.isdigit() else y for y in l]

def toNumber(y):
    try:
        return int(y)
    except:
        return long(y) # python 2

class SlideShow:
    def __init__(self, inputPath):
        self.currentIndex = -1;
        self.startCurrentIndex = -1;
        if inputPath.startswith("file://"):
            inputPath = inputPath[7:]
            inputPath = urllib2.unquote(inputPath)
        self.inputPath = inputPath
        self.inputDir = self.inputPath
        inputFile = None
        if os.path.isfile(self.inputPath):
            self.inputDir,inputFile = os.path.split(self.inputPath)
        self.currentIndex = 0
        allData = os.listdir(self.inputDir)
        if (allData == None) or (len(allData) <= 0):
            return;
        allData = sorted(allData, key = stringSplitByNumbers)
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
                if not canAdd: continue
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
        if not self.hasFiles():
            return ''
        return "[{0} / {1}] ".format(self.currentIndex + 1, len(self.files))

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
        if not config.loop:
            return
        self.currentIndex -= 1
        if self.currentIndex < 0:
            self.currentIndex = len(self.files) - 1
        if (not config.loop) and (self.startCurrentIndex == self.currentIndex):
            raise StopIteration
        return self.getCurrent()
        
    def moveFirst(self, first):
        if not self.hasFiles():
            raise StopIteration
        if not config.loop:
            return
        self.currentIndex = 0
        if not first:
            self.currentIndex = len(self.files) - 1
        return self.getCurrent()
     
    def removeCurrent(self):
        if not self.hasFiles():
            raise StopIteration
        del self.files[self.currentIndex]
        if len(self.files) <= 0:
            self.currentIndex = -1
            raise StopIteration
        if self.currentIndex == len(self.files):
            self.currentIndex = 0;

class Display:
    def __init__(self, root):
        self.root = root
        self.masterimage = None
        self.photoimage = None
        self.imageId = -1
        self.textId = -1
        self.defaultZoom = config.defaultZoom
        self.zoom = self.defaultZoom
        self.grayScale = False
        self.rotate = 0
        self.currentFile = None
        self.display = Canvas(root, bg='black', borderwidth=0, highlightthickness=0)
        self.display.pack(expand = YES, fill = BOTH)

    def clearImage(self, reloadImage):
        if self.imageId > 0:
            self.display.itemconfig(self.imageId, image=None)
        if self.textId > 0:
            self.display.itemconfig(self.textId, text='')
        self.photoimage = None
        self.root.config(cursor='tcross')
        if reloadImage:
            self.masterimage = None

    def hasValidImage(self):
        return (self.photoimage != None)
        
    def _rotateImage(self, img):
        if self.rotate == 90:
            return img.transpose(Image.ROTATE_270)
        elif self.rotate == 180:
            return img.transpose(Image.ROTATE_180)
        elif self.rotate == 270:
            return img.transpose(Image.ROTATE_90)
        else:
            return img.copy()
        #return img.rotate(self.rotate, Image.NEAREST, 1)

    def _zoomImage(self, img, w, h):
        if self.zoom < -3:
            self.zoom = -3
        if self.zoom > 100:
            self.zoom = 100
        if self.zoom == 0:
            self.zoom = -3
        text = str(self.zoom) + "%"
        originalWidth = img.size[0]
        if self.zoom == -3:
            text = 'Fit'
            img.thumbnail((w, h), Image.BILINEAR) #ANTIALIAS
        elif self.zoom == -2:
            text = 'Scale'
            r = min(float(w) / img.size[0], float(h) / img.size[1])
            img = img.resize((int(img.size[0] * r), int(img.size[1] * r)), Image.BILINEAR)
        elif self.zoom == -1:
            text = 'Fill'
            img = img.resize((w, h), Image.BILINEAR)
        currentZoom = int((float(img.size[0]) / originalWidth) * 100);
        if currentZoom != self.zoom:
            text += " " + str(currentZoom) + "%"
        return img, text      

    def setImage(self, file, extra, reloadImage = True):
        #print(file)
        if reloadImage:
            self.zoom = self.defaultZoom
            self.rotate = 0
        self.clearImage(reloadImage)
        if file == None:
            return
        self.currentFile = file
        self.extra = extra
        text = os.path.basename(file)
        if self.extra != None:
            text = self.extra + text
        # set image
        try:
            if (self.masterimage == None) or reloadImage:
                self.masterimage = Image.open(file)
                #print(file)
            w, h = self.display.winfo_width(), self.display.winfo_height()
            text += " [{0[0]}x{0[1]}]".format(self.masterimage.size)
            img = self._rotateImage(self.masterimage)
            img, zoomText = self._zoomImage(img, w, h)
            text += " " + zoomText
            if self.grayScale:
                img = img.convert('L')
                text += " Gray"
            self.setCursor()
            self.photoimage = PhotoImage(img)
            if self.imageId < 0:
                self.imageId = self.display.create_image(0, 0)
            self.display.coords(self.imageId, w // 2, h // 2)
            self.display.itemconfig(self.imageId, image=self.photoimage, anchor=CENTER)
            self.hasImage = True
        except Exception as ex:
            text += ' Error: ' + str(ex)
            self.root.config(cursor='tcross')
        # set text
        if self.textId < 0:
            self.textId = self.display.create_text(4, 4)
        self.display.itemconfig(self.textId, text=text, anchor=NW, fill='red')
        self.display.lift(self.textId)

    def setCursor(self):
        if not self.panAllowed():
            self.root.config(cursor='tcross')
        else:
            self.root.config(cursor='cross')

    def switchGrayScale(self):
        if not self.hasValidImage(): return
        self.grayScale = not self.grayScale
        self.zoom = self.defaultZoom
        self.setImage(self.currentFile, self.extra, False)
    
    def rotateDefaultZoomMode(self):
        z = self.defaultZoom + 1
        if z >= 0:
            z = -3
        self.setDefaultZoomMode(z)
    
    def setDefaultZoomMode(self, zoom):
        self.defaultZoom = zoom
        if self.zoom != self.defaultZoom:
            self.zoom = self.defaultZoom
            self.setImage(self.currentFile, self.extra, False)
    
    def switchZoom(self):
        if not self.hasValidImage():
            return
        if self.zoom < 100:
            self.zoom = 100
        else:
            self.zoom = self.defaultZoom
        self.setImage(self.currentFile, self.extra, False)
        
    def setZoom(self, original):
        z = self.zoom
        if original:
            z = 100
        else:
            z = self.defaultZoom
        if z != self.zoom:
            self.zoom = z
            self.setImage(self.currentFile, self.extra, False) 
    
    def panAllowed(self):
        return self.zoom == 100

    def moveImage(self, dx, dy):
        if not self.hasValidImage() or not self.panAllowed(): return
        self.display.move(self.imageId, dx, dy)

    def rotateImage(self, cw=True):
        if not self.hasValidImage(): return
        if cw:
            self.rotate += 90
        else:
            self.rotate -= 90
        if self.rotate >= 360:
            self.rotate -= 360
        if self.rotate < 0:
            self.rotate += 360
        self.setImage(self.currentFile, self.extra, False)

class Application:
    def __init__(self, root):
        self.fullScreen = False
        self.shiftOn = False
        self.inMouseWheel = False
        self.userCommands = None
        self.autoSlideOn = False
        self.mstart = (-1, -1)
        self.slide = None
        self.root = root
        self.root.wm_title("Image Viewer")
        self.root.config(bg='black', borderwidth=0, cursor="tcross", relief=SOLID)
        self.root.geometry("640x480")
        self.root.resizable(width=FALSE, height=FALSE)
        self.display = Display(root)
        self.root.bind("<Escape>", quit)
        self.root.bind("q", quit)
        self.root.bind("<space>", lambda e:  self.showNext(e, True))
        self.root.bind("<Down>", lambda e: self.showNext(e, True))
        self.root.bind("<Return>", lambda e: self.showNext(e, True))
        self.root.bind("<Home>", lambda e: self.showFirst(True))
        self.root.bind("<End>", lambda e: self.showFirst(False))
        #self.root.bind("<Button-3>", lambda e: self.showNext(e, True))
        self.root.bind("<Up>", lambda e: self.showNext(e, False))
        self.root.bind("<Right>", lambda e: self.display.setZoom(True))
        self.root.bind("<Left>", lambda e: self.display.setZoom(False))
        self.root.bind("z", lambda e: self.display.rotateDefaultZoomMode())
        self.root.bind("g", lambda e: self.display.switchGrayScale())
        self.root.bind("<Button-1>", self._mouseDown)
        self.root.bind("<ButtonRelease-1>", self._mouseUp)
        self.root.bind("<Configure>", self._resize)
        self.root.bind("o", lambda e: self._reinitFiles())
        self.root.bind("d", lambda e: self._deleteCurrent())
        self.root.bind("<Delete>", lambda e: self._deleteCurrent())
        self.root.bind("<Button-3>", lambda e: self.display.switchZoom())
        self.root.bind("r", self._rotateRight)
        self.root.bind("f", lambda e: self.onSwitchFullScreen())
        self.root.bind("<Shift-R>", self._rotateLeft)
        self.root.bind("h", lambda e: self.appHelp())
        self.root.bind("?", lambda e: self.appHelp())
        for i in range(1, 10):
            self.root.bind(str(i), self.runUserCommand)
        self.root.bind("<F1>", lambda e: self.appHelp())
        self.root.bind("s", lambda e: self.autoSlide())
        self.root.bind("<Shift-Left>", lambda e: self.display.moveImage(20, 0))
        self.root.bind("<Shift-Right>", lambda e: self.display.moveImage(-20, 0))
        self.root.bind("<Shift-Up>", lambda e: self.display.moveImage(0, 20))
        self.root.bind("<Shift-Down>", lambda e: self.display.moveImage(0, -20))
        self.root.bind("<KeyPress>", self.handleKeyPress)
        self.root.bind("<KeyRelease>", self.handleKeyRelease)
        #http://www.daniweb.com/software-development/python/code/217059/using-the-mouse-wheel-with-tkinter-python
        # with Windows OS
        self.root.bind("<MouseWheel>", self.mouseWheel)
        # with Linux OS
        self.root.bind("<Button-4>", self.mouseWheel)
        self.root.bind("<Button-5>", self.mouseWheel)

    def run(self, inputPath):
        if config.fullScreen:
            self.switchFullScreen()
        self.inputPath = inputPath
        self._initFiles(inputPath)
        self.display.defaultZoom = config.defaultZoom
        self.display.zoom = self.display.defaultZoom
        self.root.focus_set()
        self.root.focus_force()
        self.root.mainloop()
    
    def switchFullScreen(self):
        self.fullScreen = not self.fullScreen
        if self.fullScreen:
            w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            self.root.geometry("%dx%d+0+0" % (w, h))
            #self.root.overrideredirect(1)
            self.root.attributes('-fullscreen', True)
        else:
            self.root.geometry("640x480")
            self.root.attributes('-fullscreen', False)
        self.root.resizable(width=FALSE, height=FALSE)
    
    def onSwitchFullScreen(self):
        self.switchFullScreen()
        self.root.after(150, lambda: self.showCurrent(False))

    def handleKeyPress(self, e):
        self.autoSlideStop()
        self.shiftOn = False
        if e.keysym in ( 'Shift_L', 'Shift_R'):
            self.shiftOn = True

    def handleKeyRelease(self, e):
        self.shiftOn = False

    def cleanupMouseWheelState(self):
        self.inMouseWheel = False

    def mouseWheel(self, e):
        if self.autoSlideOn: return
        if not self.display.panAllowed():
            if self.inMouseWheel:
                return
            self.inMouseWheel = True
            self.root.after(500, lambda: self.cleanupMouseWheelState())
        if e.num == 5 or e.delta == -120:
            if not self.display.panAllowed():
                self.showNext(e, True)
                return
            if self.shiftOn:
                self.display.moveImage(-20, 0)
            else:
                self.display.moveImage(0, -20)
        if e.num == 4 or e.delta == 120:
            if not self.display.panAllowed():
                self.showNext(e, False)
                return
            if self.shiftOn:
                self.display.moveImage(20, 0)
            else:
                self.display.moveImage(0, 20)

    def runUserCommand(self, e):
        if self.userCommands == None: return
        try:
            self.userCommands.runCommand(int(e.char) - 1, self.slide.getCurrent())
        except Exception as ex:
            showerror("Image Viewer Error", str(ex))
            print(ex)

    def _rotateRight(self, e):
        self.autoSlideStop()
        self.display.rotateImage()
        
    def _rotateLeft(self, e):
        self.autoSlideStop()
        self.display.rotateImage(False)

    def _deleteCurrent(self):
        self.autoSlideStop()
        try:
            if not askokcancel("Confirm File Delete", "Delete (cannot be undone):\n" + self.slide.getCurrent()):
                return
            os.remove(self.slide.getCurrent())
            self.slide.removeCurrent()
            self.showCurrent()
        except StopIteration:
            quit(None)
        except Exception as ex:
            showerror("Image Viewer Error", str(ex))
            print(ex)

    def _reinitFiles(self):
        self.autoSlideStop()
        inputPath = askopenfilename(initialdir=self.slide.inputDir)
        self.root.focus_set()
        self.root.focus_force()
        if not inputPath: return
        self._initFiles(inputPath)

    def _initFiles(self, inputPath):
        self.slide = SlideShow(inputPath)
        self.root.after(200, lambda: self.showCurrent())

    def _resize(self, e):
        pass
        #if not self.fullScreen:
        #self.showCurrent(False)

    def _mouseDown(self, e):
        self.mstart = (e.x, e.y)

    def _mouseUp(self, e):
        if self.display.zoom != 100:
            return
        self.display.moveImage(e.x - self.mstart[0], e.y - self.mstart[1])

    def showFirst(self, first):
        if self.slide == None: return
        try:
            self.slide.moveFirst(first)
            self.showCurrent()
        except StopIteration:
            quit(e)
        except Exception as ex:
            print(ex)
            
    def showNext(self, e, down):
        if self.slide == None: return
        try:
            if down:
                self.slide.moveNext()
            else:
                self.slide.movePrevious()
            self.showCurrent()
        except StopIteration:
            quit(e)
        except Exception as ex:
            print(ex)

    def showCurrent(self, reloadImage = True):
        global config
        if self.slide == None: return
        try:
            self.display.setImage(self.slide.getCurrent(), self.slide.getExtra(), reloadImage)
            if config.autoSlideAutoStart:
                config.autoSlideAutoStart = False
                self.root.after(config.autoSlideTime, lambda: self.autoSlide())
        except Exception as ex:
            print(ex)
            if config.autoSlideAutoStart:
                quit(None)

    def autoSlide(self):
        self.autoSlideOn = not self.autoSlideOn
        if self.autoSlideOn:
            self.showNext(None, True)
            self.root.after(config.autoSlideTime, lambda: self.autoSlideNext())

    def autoSlideNext(self):
        if not self.autoSlideOn: return
        self.showNext(None, True)
        self.root.after(config.autoSlideTime, lambda: self.autoSlideNext())

    def autoSlideStop(self):
        self.autoSlideOn = False

    def appHelp(self):
        self.autoSlideStop()
        extra = None
        if self.userCommands != None:
            extra = self.userCommands.listCommands()
        showHelp(extra)
        
class UserCommands:
    def __init__(self, commandsFile):
        self.commands = None
        if (commandsFile != None) and os.path.isfile(commandsFile):
            with open(commandsFile) as f:
                self.commands = f.readlines()
    
    # quit|separator|commandParts
    def parseCommand(self, command, currentFile):
        if (command == None) or (len(command) <= 0): return None
        parts = command.strip('\r\n \t').split('|', 3);
        if len(parts) < 3: return None
        shouldQuit = parts[0].strip() == 'quit'
        commandParts = parts[2].split(parts[1])
        for i, p in enumerate(commandParts):
            p = p.strip()
            if currentFile != None:
                p = p.replace("%f%", currentFile)
            commandParts[i] = p
        return (shouldQuit, commandParts)
    
    def runCommand(self, commandIndex, currentFile):
        if currentFile == None: return
        if (self.commands == None) or (len(self.commands) == 0) or commandIndex >= len(self.commands): return
        commandText = self.commands[commandIndex]
        command = self.parseCommand(commandText, currentFile)
        if command == None: return
        commandText = " ".join(command[1])
        text = "Run"
        if command[0]:
            text += " and quit"
        if not askokcancel("Confirm Command", text + ":\n" + commandText):
                return
        #subprocess.call(command[1], shell=False)
        subprocess.Popen(command[1], shell=False)
        if command[0]:
            quit(None)
    
    def listCommands(self):
        if (self.commands == None) or (len(self.commands) == 0): return ""
        res = "Custom commands (key command):\n"
        for i, c in enumerate(self.commands):
            if i > 9: break
            command = self.parseCommand(c, None)
            if command == None: continue
            commandText = " ".join(command[1])
            if command[0]: commandText += " # quit after run"
            res += " {0} {1}\n".format(i + 1, commandText)
        return res

def quit(e):
    root.destroy()

def main(root):
    global config
    try:
        app = Application(root)
        inputPath = os.getcwd()
        i = 1
        while i < len(sys.argv):
            arg = sys.argv[i]
            i += 1
            if arg[0] == '-':
                targ = arg[1:].lower()
                if targ == '?' or targ == "-help":
                    showHelp()
                    return
                elif targ == 'w':
                    config.fullScreen = False
                elif targ == 'd':
                    config.detectImages = True
                elif targ == 'l':
                    config.loop = False
                elif targ == 's':
                    config.autoSlideAutoStart = True
                elif targ == 'st':
                    try:
                        config.autoSlideTime = int(sys.argv[i])
                        config.autoSlideTime = config.autoSlideTime * 1000
                        if config.autoSlideTime <= 0:
                            config.autoSlideTime = 3000
                    except Exception as ex:
                        print(ex)
                        config.autoSlideTime = 3000
                    i += 1
                elif targ == 'c':
                    app.userCommands = UserCommands(sys.argv[i])
                    i += 1
                elif targ == 'z':
                    if sys.argv[i] == 'fit':
                        config.defaultZoom = -3
                    elif sys.argv[i] == 'scale':
                        config.defaultZoom = -2
                    elif sys.argv[i] == 'fill':
                        config.defaultZoom = -1 
                    else:
                        raise Exception("Unknown default zoom mode: " + sys.argv[i])
                    i += 1
                else:
                    raise Exception("Unknown option: " + arg + "\nUse -? for help")
            else:
                inputPath = arg
        app.run(inputPath)
    except Exception as ex:
        showerror("Image Viewer Error", str(ex))
        print(ex)
        
class HelpBox(Toplevel):

    def __init__(self, root, extra = None):
        Toplevel.__init__(self, root)
        self.root = root
        self.title("Image Viewer Help")
        self.geometry("480x360")
        self.resizable(width=FALSE, height=FALSE)
        self.maxsize(width=480, height=360)
        self.bind("<Escape>", self.cancel)
        self.bind("q", self.cancel)
        self.bind("<F1>", self.cancel)
        self.bind("h", self.cancel)
        text = Text(self)
        scrollbar = Scrollbar(self)
        scrollbar.pack(side=RIGHT, fill=Y)
        scrollbar.config(command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        data = """http://madebits.com Press Esc key or right-click to close help.

miv.pyw [OPTIONS] pathToFileOrFolder

Command-line options:
 -?\t\tshow this help
 -d\t\tdetect image files (a bit slower)
 -w\t\tshow window border (640x480)
 -l\t\tloop only once forward (previous not allowed)
 -s\t\tauto start slideshow
 -st timeInSeconds for auto start slideshow (default 3)
 -z fit | scale | fill sets default zoom mode
 -c customCommandsFile
 
Application commanding keys:
 F1 or h\t\tshow / hide this help
 Esc or q\t\tquit
 Space or Down or Enter
 \t\tnext file
 Up\t\tprevious file
 Right\t\tzoom 100%
 Left\t\tzoom default (fit)
 z\t\tswitch default zoom fit / scale / fill
 r\t\trotate 90 degrees right
 Shift+r\t\trotate 90 degrees left
 g\t\tswitch grayscale filter
 s\t\tswitch auto slideshow
 o\t\topen a new file
 f\t\tswitch fullscreen
 Del or d\t\tdelete current file
 Shift+arrows\t\ton 100% zoom pan image

Mouse:
 Right\t\tswitch zoom 100% / default (fit)
 Left\t\ton 100% zoom drag to pan image
 Wheel\t\tmove next / previous
      \t\ton 100% zoom pan up / down
      \t\tor with Shift key left / right
"""
        if extra != None:
            data += '\n' + extra + '\n'
        data += """Custom commands file can contain up to 9 lines mapped
to keyboard keys 1 to 9 with custom commands of form:
quit|separator|commandPartsSeparatedWithSeparator
 quit is optional if set the application exits after command
 %f% in commandParts is replaced with current file path

Examples: 
quit|,|pinta,%f%
|,|pcmanfm,-w,%f%
"""
        text.insert(INSERT, data)
        text.config(state=DISABLED)
        text.bind("<Button-3>", self.cancel)
        text.pack(side=LEFT, fill=Y)
        # modal
        self.focus_set()
        self.grab_set()
        self.transient(root)
        self.wait_window(self)

    def cancel(self, event=None):
        self.root.focus_set()
        self.destroy()

def showHelp(extra = None):
    hlp = HelpBox(root, extra)
    return

if __name__ == '__main__':
    main(root)

#eof

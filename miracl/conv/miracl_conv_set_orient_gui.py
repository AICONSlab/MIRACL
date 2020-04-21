#!/usr/bin/env python

# coding: utf-8

import matplotlib

matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import Tkinter as Tk
import tkFileDialog
import tkMessageBox as messagebox
import glob
import os
import sys
import cv2

root = Tk.Tk()
root.withdraw()
indir = tkFileDialog.askdirectory(title='Open clarity dir (with .tif files) by double clicking then "Choose"')

assert isinstance(indir, str)

if not os.path.exists(indir):
    sys.exit('%s does not exist ... please check path and rerun script' % indir)

flist = glob.glob(os.path.join(indir, '*.tif*'))
# flist = glob.glob('%s/*.tif' % indir)

root.deiconify()
root.configure(background='black')
root.geometry("1250x1000")
root.wm_title("Input Tiff files")


# -------------------------------

def ortbutton():
    ort = Tk.Menubutton(root, text="Orientation", justify=Tk.CENTER)
    ort.grid()
    ort.menu = Tk.Menu(ort, tearoff=0)
    ort["menu"] = ort.menu
    AOVar = Tk.IntVar()
    SOVar = Tk.IntVar()
    COVar = Tk.IntVar()
    ort.menu.add_checkbutton(label="Axial", variable=AOVar)
    ort.menu.add_checkbutton(label="Sagittal", variable=SOVar)
    ort.menu.add_checkbutton(label="Coronal", variable=COVar)

    return AOVar, SOVar, COVar


def leftbutton():
    mb = Tk.Menubutton(root, text="Annotation (Into Page)", justify=Tk.CENTER)
    mb.grid(row=5, column=0)
    mb.menu = Tk.Menu(mb, tearoff=0)
    mb["menu"] = mb.menu
    SLVar = Tk.IntVar()
    ILVar = Tk.IntVar()
    RLVar = Tk.IntVar()
    LLVar = Tk.IntVar()
    ALVar = Tk.IntVar()
    PLVar = Tk.IntVar()
    mb.menu.add_checkbutton(label="Superior", variable=SLVar)
    mb.menu.add_checkbutton(label="Inferior", variable=ILVar)
    mb.menu.add_checkbutton(label="Right", variable=RLVar)
    mb.menu.add_checkbutton(label="Left", variable=LLVar)
    mb.menu.add_checkbutton(label="Anterior", variable=ALVar)
    mb.menu.add_checkbutton(label="Posterior", variable=PLVar)

    return SLVar, ILVar, RLVar, LLVar, ALVar, PLVar


def topbutton():
    mb2 = Tk.Menubutton(root, text="Annotation", justify=Tk.CENTER)
    mb2.grid(row=0, column=1, pady=4)
    mb2.menu = Tk.Menu(mb2, tearoff=0)
    mb2["menu"] = mb2.menu
    STVar = Tk.IntVar()
    ITVar = Tk.IntVar()
    RTVar = Tk.IntVar()
    LTVar = Tk.IntVar()
    ATVar = Tk.IntVar()
    PTVar = Tk.IntVar()
    mb2.menu.add_checkbutton(label="Superior", variable=STVar)
    mb2.menu.add_checkbutton(label="Inferior", variable=ITVar)
    mb2.menu.add_checkbutton(label="Right", variable=RTVar)
    mb2.menu.add_checkbutton(label="Left", variable=LTVar)
    mb2.menu.add_checkbutton(label="Anterior", variable=ATVar)
    mb2.menu.add_checkbutton(label="Posterior", variable=PTVar)

    return STVar, ITVar, RTVar, LTVar, ATVar, PTVar


def rightbutton():
    mb3 = Tk.Menubutton(root, text="Annatation", justify=Tk.CENTER)
    mb3.grid(row=5, column=3, padx=50)
    mb3.menu = Tk.Menu(mb3, tearoff=0)
    mb3["menu"] = mb3.menu
    SRVar = Tk.IntVar()
    IRVar = Tk.IntVar()
    RRVar = Tk.IntVar()
    LRVar = Tk.IntVar()
    ARVar = Tk.IntVar()
    PRVar = Tk.IntVar()
    mb3.menu.add_checkbutton(label="Superior", variable=SRVar)
    mb3.menu.add_checkbutton(label="Inferior", variable=IRVar)
    mb3.menu.add_checkbutton(label="Right", variable=RRVar)
    mb3.menu.add_checkbutton(label="Left", variable=LRVar)
    mb3.menu.add_checkbutton(label="Anterior", variable=ARVar)
    mb3.menu.add_checkbutton(label="Posterior", variable=PRVar)

    return SRVar, IRVar, RRVar, LRVar, ARVar, PRVar


[AOVar, SOVar, COVar] = ortbutton()
[SLVar, ILVar, RLVar, LLVar, ALVar, PLVar] = leftbutton()
[SRVar, IRVar, RRVar, LRVar, ARVar, PRVar] = rightbutton()
[STVar, ITVar, RTVar, LTVar, ATVar, PTVar] = topbutton()

# -------------------------------

print('\n Reading images and automatically adjusting contrast \n')

n = len(flist)

global index
index = int(n / 2.0)

f = Figure(figsize=(8, 8), dpi=100, facecolor='royalblue', edgecolor='white', linewidth=2)
a = f.add_subplot(111)
img = cv2.imread(flist[index], 0)
clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
cl = clahe.apply(img)
a.imshow(cl, 'gray')
a.axis('off')
a.set_title(os.path.basename(flist[index]), color='white', y=1.05, fontsize=10)

# a tk.DrawingArea
canvas = FigureCanvasTkAgg(f, master=root)
canvas.show()

# creating frame for toolbar
frame = Tk.Frame(root)
toolbar = NavigationToolbar2TkAgg(canvas, frame)
toolbar.update()
toolbar.grid(row=8, column=1, padx=4, pady=4, sticky="e")

canvas._tkcanvas.grid(row=5, column=1, sticky="w")
canvas._tkcanvas.configure(background='black', highlightcolor='black', highlightbackground='black')


def on_key_event(event):
    print('you pressed %s' % event.key)
    key_press_handler(event, canvas, toolbar)


# canvas.mpl_connect('key_press_event', on_key_event)

def _quit():
    root.quit()  # stops mainloop
    root.destroy()


def nextframe(i=1, imgnum=-1):
    global index

    if imgnum == -1:
        index += i
    else:
        index = imgnum - 1
    if index >= len(flist):
        index = 0
    elif index < 0:
        index = len(flist) - 1

    evar.set(index + 1)

    return index


# def getimgnum(event=None):
#     nextframe(imgnum=evar.get())

def nextimg():
    index = nextframe(1)
    img = cv2.imread(flist[index], 0)
    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
    cl = clahe.apply(img)
    a.imshow(cl, 'gray')
    a.axis('off')
    a.set_title(os.path.basename(flist[index]), fontsize=10)
    canvas.draw()


def previmg():
    index = nextframe(-1)
    img = cv2.imread(flist[index], 0)
    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
    cl = clahe.apply(img)
    a.imshow(cl, 'gray')
    a.axis('off')
    a.set_title(os.path.basename(flist[index]), fontsize=10)
    canvas.draw()


# Go to number
def gotoimg(event=None):
    index = nextframe(imgnum=evar.get())
    img = cv2.imread(flist[index], 0)
    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
    cl = clahe.apply(img)
    a.imshow(cl, 'gray')
    a.axis('off')
    a.set_title(os.path.basename(flist[evar.get() - 1]), fontsize=10)
    canvas.draw()


fr = Tk.Frame(root)
fr.grid(row=7, column=1, padx=4, pady=4)

prevbutton = Tk.Button(master=root, text='Prev image', command=lambda: previmg())
prevbutton.grid(row=7, column=1, sticky="w", padx=4, pady=4)

ilabel = Tk.Label(fr, text="image number:")
ilabel.grid(row=7, column=2, padx=4, pady=4)

evar = Tk.IntVar()
evar.set(1)

entry = Tk.Entry(fr, textvariable=evar)
entry.grid(row=7, column=3, pady=4)
entry.bind('<Return>', gotoimg)

nxtbutton = Tk.Button(master=root, text='Next image', command=lambda: nextimg())
nxtbutton.grid(row=7, column=1, sticky="e", padx=4, pady=4)


def on_closing():
    if messagebox.askokcancel("Quit", "Done setting orientation, want to quit?"):
        root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()

# -------------------------------

# Get orientation and annotations

# Axial
if AOVar.get() == 1:
    ort = list('ARS')

    # get Top
    if ATVar.get() == 1:
        ort[0] = 'A'
    elif PTVar.get() == 1:
        ort[0] = 'P'

    # get Right
    if RRVar.get() == 1:
        ort[1] = 'L'
    elif LRVar.get() == 1:
        ort[1] = 'R'

    # get into page (left button)
    if SLVar.get() == 1:
        ort[2] = 'I'
    elif ILVar.get() == 1:
        ort[2] = 'S'

# Sagittal
elif SOVar.get() == 1:
    ort = list('ASR')

    # get Top
    if ATVar.get() == 1:
        ort[0] = 'A'
    elif PTVar.get() == 1:
        ort[0] = 'P'

    # get Right
    if SRVar.get() == 1:
        ort[1] = 'I'
    elif IRVar.get() == 1:
        ort[1] = 'S'

    # get into page
    if RLVar.get() == 1:
        ort[2] = 'R'
    elif LLVar.get() == 1:
        ort[2] = 'L'

# Coronal
elif COVar.get() == 1:
    ort = list('RAS')

    # get Top
    if STVar.get() == 1:
        ort[0] = 'R'
    elif ITVar.get() == 1:
        ort[0] = 'L'

    # get Right
    if RRVar.get() == 1:
        ort[1] = 'A'
    elif LRVar.get() == 1:
        ort[1] = 'P'

    # get into page
    if ALVar.get() == 1:
        ort[2] = 'S'
    elif PLVar.get() == 1:
        ort[2] = 'I'


ortstr = ''.join(ort)

# -------------------------------

with open("ort2std.txt", "w") as myfile:
    myfile.write("tifdir=%s \nortcode=%s \n" % (indir, ortstr))


# TODOlps
# scroll bar

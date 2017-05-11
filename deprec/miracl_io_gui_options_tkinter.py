#!/usr/bin/env python

import argparse
from Tkinter import *


# Inputs #########

def helpmsg(name=None):
    return '''miracl_io_gui_options.py -t title -f fields [separated by space] -hf helpfun

Takes list of strings as options for entries for a gui options, and a gui title

example: miracl_io_gui_options.py -t "Reg options" -f orient label resolution

Input options will be printed as output

'''


parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg())
parser.add_argument('-t', '--title', type=str, help="gui title", required=True)
parser.add_argument('-f', '--fields', type=str, nargs='+', help="fields for options", required=True)
parser.add_argument('-hf', '--helpfun', type=str, help="help fun")

args = parser.parse_args()

title = args.title
fields = args.fields
helpfun = args.helpfun


def fetch(entries):
    for entry in entries:
        field = entry[0]
        text = entry[1].get()
        print('%s: "%s"' % (field, text))


def makeform(root, fields):
    entries = []
    values = []

    strlen = len(max(fields, key=len))
    strw = int(strlen * 1.2)

    for field in fields:
        row = Frame(root)
        lab = Label(row, width=strw, text=field, anchor='w')
        ent = Entry(row)
        row.pack(side=TOP, fill=X, padx=5, pady=5)
        lab.pack(side=LEFT)
        ent.pack(side=RIGHT, expand=YES, fill=X)
        entries.append((field, ent))
        values.append(ent)

    return entries, values, strw


def helpwindown(root, helpfun):
    window = Toplevel(root)
    window.title("Help func")
    T = Text(window, height=50, width=150)
    T.pack()
    T.insert(END, "%s" % helpfun)


def main():
    root = Tk()
    root.title('%s' % title)

    [ents, vals, strw] = makeform(root, fields)

    n = len(fields)
    w = strw * 10
    h = (n * 40) + 50
    root.geometry("%dx%d" % (w, h))

    root.bind('<Return>', (lambda event, e=ents: fetch(e)))

    b1 = Button(root, text='Enter',
                command=(lambda e=ents: fetch(e)))
    b1.pack(side=LEFT, padx=5, pady=5)

    b2 = Button(root, text='Done', command=root.quit)
    b2.pack(side=RIGHT, padx=5, pady=5)

    b3 = Button(root, text="Help func", command=lambda: helpwindown(root, helpfun))
    b3.pack(side=LEFT, padx=5, pady=5)

    root.mainloop()

    # with open("opts.txt", "w") as myfile:
    #    for o in range(len(fields)):
    #       myfile.write("%s\n" % vals[o].get())


if __name__ == '__main__':
    main()

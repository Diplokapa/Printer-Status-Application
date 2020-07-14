import PrinterOOP as p
from tkinter import *
import easygui
import concurrent.futures
import time
import threading
from functools import partial
import webbrowser
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter import Tk
from tkinter.ttk import Progressbar


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
printer_frames = []
printers = []

root_frame = Tk()
root_frame.title("Printer Stats")
root_frame.configure(bg="black")
# root_frame.pack(fill=BOTH,expand= True)
root_frame.geometry("1600x600")
root = ScrollableFrame(root_frame)
root.pack(fill=BOTH,expand= True)
start = time.perf_counter()


def initialize():
    progressbar = Progressbar(root, orient=HORIZONTAL, length=100, mode='indeterminate')
    progressbar.pack()
    progressbar.start(10)
    print("starting")

    try:
        filepath = open("path.txt")
        file = open(filepath.read())

    except:
        file = open(easygui.fileopenbox())
        filepath = open("path.txt", "w")
        filepath.write(file.name)

    print("threading url")
    with concurrent.futures.ThreadPoolExecutor() as exe:
        exe.map(create_urls, file)
    print("done creating urls")
    with concurrent.futures.ThreadPoolExecutor() as exe:
        exe.map(update_printers, printers)

    print("done")
    finish = time.perf_counter()
    print(f'finished in {round(finish-start,2)} seconds')
    root_frame.title(f'Printer Stats {datetime.now()}')
    print(len(root.winfo_children()))
    for frames in printer_frames:
        frames.destroy()
    printer_frames.clear()
    create_frames()
    progressbar.stop()
    progressbar.destroy()

def create_urls(line):
    printers.append(p.get_printer_model(line))


def update_printers(printer):

    printer.update()
    printer.print_status()


def create_printer_frame(model,ip,location,toner,drum,alert,index, indexY ):
    if model =="offline" or model =="OFFLINE":
        bgcolor ="RED"
    else:
        bgcolor="BLACK"
    frame = Frame(root.scrollable_frame,bg=bgcolor,borderwidth=2)
    frame.grid(row=index,column=indexY, padx= 5,pady=5)
    modelLabel = Label(frame, width=35, text=("Model: "+model), borderwidth=2, bg="white", anchor="w", relief="raised")
    ipLabel = Button(frame, width=35, text=("Ip: "+ip.strip()), borderwidth=2, bg="grey", anchor="w", relief="raised", command=partial(ip_click,ip))
    locationLabel = Label(frame, width=35, text=(location), borderwidth=2, bg="grey", anchor="w", relief="raised")
    intToner = ''.join((x for x in toner if x.isdigit()))
    if intToner:
        if int(str(intToner)[:2]) < 25:
           if int(str(intToner)[:2]) < 10:
                toner_color = "red"
           else:
            toner_color = "pink"
        else:
            toner_color ="grey"
    else:
        toner_color = "red"
    tonerLabel = Label(frame, width=35, text=("Toner level: "+toner), borderwidth=2, bg=toner_color, anchor="w", relief="raised")
    drumToner = ''.join((x for x in drum if x.isdigit()))
    if drumToner:
        if int(str(drumToner)[:2]) < 25:
            if int(str(drumToner)[:2]) < 10:
                print(drumToner)
                drum_color = "red"
            else:
                drum_color = "pink"
        else:
            drum_color = "grey"
    else:
        drum_color = "red"
    drumLabel = Label(frame, width=35, text=("Drum level: " + drum), borderwidth=2, bg=drum_color, anchor="w", relief="raised")
    alertLabel = Label(frame, width=35, text=("Alerts: "+alert), borderwidth=2, bg="grey", anchor="w", relief="raised")
    # modelLabel.grid(row=0, column=0, columnspan=1)
    # ipLabel.grid(row=0, column=1, columnspan=1)
    # locationLabel.grid(row=1, column=0, columnspan=1)
    # tonerLabel.grid(row=1, column=1, columnspan=1)
    # drumLabel.grid(row=2, column=0, columnspan=1)
    # alertLabel.grid(row=2, column=1, columnspan=1)
    ipLabel.pack()
    modelLabel.pack()

    locationLabel.pack()
    tonerLabel.pack()
    drumLabel.pack()
    alertLabel.pack()

    printer_frames.append(frame)


def ip_click(ip):

    url = ("http://"+ip.strip())
    webbrowser.open(url)


def refresh_all():

    printers.clear()

    t1 = threading.Thread(target=initialize)
    t1.start()


def refresh_button():
    refresh_all()


def create_frames():
    index = 0
    indexY = 0
    for printer in printers:
        create_printer_frame(printer.model, printer.ip, printer.location, printer.toner,
                             printer.drum, printer.alert, index, indexY)
        # printer_menu.add_command(label=(printer.model + ": " + printer.ip))

        root.update_idletasks()
        root.update()
        if indexY == 4:
            index += 1
            indexY = 0
        else:
            indexY += 1


def print_frames():
    print(len(printer_frames))


def initiliaze_gui(root):
    print("starting gui")
    my_menu=Menu(root)
    root_frame.config(menu=my_menu)

    file_menu=Menu(my_menu, tearoff=0)
    global printer_menu
    printer_menu = Menu(my_menu, tearoff=0)
    my_menu.add_cascade(label="File", menu=file_menu)
    # my_menu.add_cascade(label="Printers", menu=printer_menu)

    file_menu.add_command(label="Exit", command=root_frame.quit)
    file_menu.add_command(label="Refresh ALL", command=refresh_button)
    file_menu.add_command(label="print Frame",command=print_frames)
    root_frame.update()

print("just before gui")
initiliaze_gui(root)

t1 = threading.Thread(target=initialize)
t1.start()
# with concurrent.futures.ThreadPoolExecutor() as exe:
#     exe.submit(initialize)

#




root_frame.mainloop()



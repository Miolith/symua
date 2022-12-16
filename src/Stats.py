import math
import numpy as np
from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

class Observer:
    def __init__(self):
        self.event_list = {}
        self.event_maxy = {}

    def create_event(self, name, default=None):
        if default is None:
            self.event_list[name] = []
            self.event_maxy[name] = 0
        else:
            self.event_list[name] = default
            self.event_maxy[name] = max(default)
    def append_data(self, name, data):
        data_id = len(self.event_list[name])
        self.event_list[name].append(data)
        if self.event_maxy[name] < data:
            self.event_maxy[name] = data
        return data_id

    def edit_data(self, name, data_id, new_data):
        self.event_list[name][data_id] = new_data


class StatisticWindow:
    def __init__(self, Tk, observer, watching_id):
        self.window = Toplevel(Tk)
        self.event_manager = observer
        self.watching_id = watching_id


        self.fig = plt.Figure()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.get_tk_widget().pack()

        self.anims = []
        self.tracks = []
        self.axs = []
        self.track_event(list(self.event_manager.event_list.keys())[watching_id])
        

    def animate(self, idx):
        name = "nest_population_"+str(self.watching_id)
        ev = self.event_manager.event_list[name]
        elem = self.tracks[idx]
        size = len(ev)
        elem.set_xdata(np.arange(0, size, 1))
        elem.set_ydata(ev)
        self.axs[idx].set_xlim(xmax=size)
        self.axs[idx].set_ylim(ymax=self.event_manager.event_maxy[name] + 1)

    def track_new_event(self, event_name, new_watching_id):
        self.text["text"] = f"Tracking of {event_name}"
        self.fig.close()
        self.anims.clear()
        self.tracks.clear()
        self.axs.clear()
        self.watching_id = new_watching_id
        self.track_event(event_name)


    def track_event(self, event_name):
        self.text = Label(self.window, text=f"Tracking of {event_name}")
        self.text.pack(side=TOP)
        event = self.event_manager.event_list[event_name]
        ax = self.fig.add_subplot()
        x = np.arange(0, len(event), 1)
        line, = ax.plot(x, event)
        ax.set_ylim(ymin=0)
        ax.set_xlim(xmin=0)
        self.axs.append(ax)
        self.tracks.append(line)
        self.anims.append(animation.FuncAnimation(self.fig, lambda x: self.animate(0), interval=1000))





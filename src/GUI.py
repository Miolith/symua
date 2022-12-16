from tkinter import *
from tkinter import ttk
from Stats import *
from environment import *

class GUI:
    REFRESH_RATE = 30
    def __init__(self, width, height, model):
        self.model = model

        self.started = False
        self.step_speed = 5
        self.step_counter = 0
        self.agent_circle_width = 4
        self.food_circle_width = 10
        
        self.phero_pos = []
        self.strats = [0]

        self.tk = Tk()
        
        self.phero_track = IntVar()

        self.can = Canvas(self.tk, width=width, height=height)
        self.can.pack(side=TOP)

        self.user_frame = Frame(self.tk)
        self.user_frame.pack(side=BOTTOM)

        self.__setup_user_frame()
        self.stats_win = []

        self.stats_win.append(StatisticWindow(self.tk, self.model.event_manager, 0))


        self.tk.mainloop()

    def reset_sim(self):
        self.phero_pos = []
        for tracker in range(self.model.nest_nb):
            self.stats_win[tracker].window.destroy()
        self.stats_win = []
        model = AntsModel(2, 800, 600)
        self.model = model
        for tracker in range(self.model.nest_nb):
            self.stats_win.append(StatisticWindow(self.tk, self.model.event_manager, tracker))
        self.step_counter = 0


    def sim_start_and_pause(self):
        self.started = not self.started
        if self.started:
            self.model.foods_nb = self.food_nb_scale.get()
            self.model.food_max_serving = self.food_scale.get()

            for k,queen in enumerate(self.model.yield_queens()):
                queen.antsSpawnRate = self.Queen_baby_cd.get()
                queen.explorer_chance = float(self.Explorer_prop.get()/100)
                queen.worker = float(self.Worker_prop.get()/100)
                queen.baby_burst = self.Queen_baby_rush_scale.get()
                queen.food_greed = self.Queen_greed_scale.get()
                queen.strat = self.strats[k]
                queen.soldier_chance = float(self.soldier_scale.get()/100)

            self.play_button["text"] = "Pause"
            self.nest_scale["state"] = "disabled"
            self.update()
            self.calc_phero()
        else:
            self.play_button["text"] = "Play"


    def __setup_user_frame(self):

        self.play_button = Button(self.user_frame, text = "Play", command = self.sim_start_and_pause)
        self.play_button.pack(side=TOP)
        self.speed_scale = Scale(self.user_frame, from_=1, to=self.REFRESH_RATE/2, orient=HORIZONTAL, length=400)
        self.speed_scale.set(self.step_speed)
        self.speed_scale.pack()

        self.phero_trace_on = Checkbutton(self.user_frame, text="Afficher les phéromones", variable=self.phero_track, onvalue=1, command=self.calc_phero)
        self.phero_trace_on.pack(side=TOP)

        self.first_line = Frame(self.user_frame)
        self.first_line.pack(side=TOP)

        self.loc_frames = [Frame(self.first_line) for _ in range(7)]
        for fr in self.loc_frames:
            fr.pack(side=LEFT)
        Label(self.loc_frames[0], text="Food number :").pack(side=TOP)

        self.food_nb_scale = Scale(self.loc_frames[0], from_=0, to=100, length=100)
        self.food_nb_scale.set(30)
        self.food_nb_scale.pack(side=TOP)

        Label(self.loc_frames[1], text="Food Qte :").pack(side=TOP)

        self.food_scale = Scale(self.loc_frames[1], from_=0, to=100, length=100)
        self.food_scale.set(30)
        self.food_scale.pack(side=TOP)

        Label(self.loc_frames[2], text="Queen ants rate(tick) :").pack(side=TOP)

        self.Queen_baby_cd = Scale(self.loc_frames[2], from_=0, to=100, length=100)
        self.Queen_baby_cd.set(20)
        self.Queen_baby_cd.pack(side=TOP)

        Label(self.loc_frames[5], text="Queen Greediness :").pack(side=TOP)

        self.Queen_greed_scale = Scale(self.loc_frames[5], from_=0, to=2, length=100, resolution=0.1)
        self.Queen_greed_scale.set(1)
        self.Queen_greed_scale.pack(side=TOP)

        Label(self.loc_frames[6], text="Queen Baby Rush :").pack(side=TOP)

        self.Queen_baby_rush_scale = Scale(self.loc_frames[6], from_=0, to=20, length=100)
        self.Queen_baby_rush_scale.set(10)
        self.Queen_baby_rush_scale.pack(side=TOP)

        Label(self.loc_frames[3], text="Explorer proportion((%) :").pack(side=TOP)

        self.Explorer_prop = Scale(self.loc_frames[3], from_=0, to=100, length=100, command=self.balance_workers)
        self.Explorer_prop.set(70)
        self.Explorer_prop.pack(side=TOP)
 
        Label(self.loc_frames[4], text="Worker proportion((%) :").pack(side=TOP)

        self.Worker_prop = Scale(self.loc_frames[4], from_=0, to=100, length=100, command=self.balance_explorer)
        self.Worker_prop.set(30)
        self.Worker_prop.pack(side=TOP)

        self.second_line = Frame(self.user_frame)
        self.second_line.pack(side=TOP)

        self.loc_frames_2 = [Frame(self.second_line) for _ in range(3)]
        for fr in self.loc_frames_2:
            fr.pack(side=LEFT)

        Label(self.loc_frames_2[0], text="Nest Number :").pack(side=TOP)

        self.nest_scale = Scale(self.loc_frames_2[0], from_=1, to=5, length=100, command=self.set_new_model)
        self.nest_scale.set(1)
        self.nest_scale.pack(side=TOP)

        Label(self.loc_frames_2[2], text="Soldier spawn chance(%) :").pack(side=TOP)

        self.soldier_scale = Scale(self.loc_frames_2[2], from_=0, to=100, length=100)
        self.soldier_scale.set(0)
        self.soldier_scale.pack(side=TOP)

        Label(self.loc_frames_2[1], text="Choose Nest Strat :").pack(side=TOP)

        self.strat_combo = ttk.Combobox(self.loc_frames_2[1], values=["Pacifist", "Aggressor", "Defender", "Coop"], state="readonly",width=10)
        self.strat_combo.current(0)
        self.strat_combo.pack(side=TOP)

        self.nest_combo = ttk.Combobox(self.loc_frames_2[1], values=["Nest_0"],state="readonly",width=10)
        self.nest_combo.current(0)
        self.nest_combo.pack(side=TOP)

        self.nest_button = Button(self.loc_frames_2[1], text="Apply Strat to Nest", command=self.apply_strat)
        self.nest_button.pack(side=TOP)

    def apply_strat(self):
        self.strats[self.nest_combo.current()] = self.strat_combo.current()


    def set_new_model(self, entry):
        for win in self.stats_win:
            win.window.destroy()
        self.stats_win = []
        nest_nb = self.nest_scale.get()
        model = AntsModel(nest_nb, 800, 600)
        self.model = model

        for tracker in range(nest_nb):
            self.stats_win.append(StatisticWindow(self.tk, self.model.event_manager, tracker))
        self.strats = [0 for _ in range(nest_nb)]
        self.nest_combo["values"] = ["Nest_"+str(i) for i in range(nest_nb)]



    def balance_workers(self, info):
        self.Worker_prop.set(100 - self.Explorer_prop.get())

    def balance_explorer(self, info):
        self.Explorer_prop.set(100 - self.Worker_prop.get())


    def show_foods(self):
        for food in self.model.foods:
            x = food.pos[0]
            y = food.pos[1]
            self.can.create_oval(x - self.food_circle_width,y - self.food_circle_width,x + self.food_circle_width,y + self.food_circle_width, fill=food.color, outline=food.color)


    def calc_phero(self):
        self.phero_pos = []
        for y in range(self.model.height):
            for x in range(self.model.width):
                if self.model.map[y][x].strength > 0:
                    val = 55 + 20*min(10, self.model.map[y][x].strength)
                    self.phero_pos.append((x,y,val))
        
        if self.phero_track.get() == 1 and self.started:
            self.tk.after(250, self.calc_phero)
    
    def show_phero(self):
        for px,py,pvalue in self.phero_pos:
            self.can.create_rectangle(px,py,px+1,py+1, fill = "#%x%x%x" % (pvalue, pvalue, pvalue))

    def show_agents(self):
        for agent in self.model.schedule.agents:
            x = agent.posi[0]
            y = agent.posi[1]
            self.can.create_oval(x - self.agent_circle_width,y - self.agent_circle_width,x + self.agent_circle_width,y + self.agent_circle_width, fill=agent.color, outline=agent.color)

    def update(self):
        self.step_speed = int(self.speed_scale.get())

        if self.step_counter % self.step_speed == 0:
            self.model.step()
            self.step_counter = 1
        else:
            self.step_counter += 1

        self.can.delete('all')
        self.show_agents()
        self.show_foods()
        if self.phero_track.get() == 1:
            self.show_phero()
        
        if self.started:
            self.tk.after(self.REFRESH_RATE, self.update)



if __name__ == "__main__":
    model = AntsModel(2,800,600)
    GUI(800,600,model)

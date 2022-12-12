from tkinter import *

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

        self.tk = Tk()
        
        self.phero_track = IntVar()

        self.can = Canvas(self.tk, width=width, height=height)
        self.can.pack(side=TOP)

        self.user_frame = Frame(self.tk)
        self.user_frame.pack(side=BOTTOM)

        self.__setup_user_frame()


        self.tk.mainloop()

    def sim_start_and_pause(self):
        self.started = not self.started
        if self.started:
            self.model.foods_nb = self.food_nb_scale.get()
            self.model.food_max_serving = self.food_scale.get()

            for queen in self.model.yield_queens():
                queen.antsSpawnRate = self.Queen_baby_cd.get()
                queen.explorer_chance = self.Explorer_prop.get()/100
                queen.worker = self.Worker_prop.get()/100

            self.play_button["text"] = "Pause"
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

        self.loc_frames = [Frame(self.user_frame) for _ in range(5)]
        for fr in self.loc_frames:
            fr.pack(side=LEFT)
        Label(self.loc_frames[0], text="Food number :").pack(side=TOP)

        self.food_nb_scale = Scale(self.loc_frames[0], from_=0, to=100, length=100)
        self.food_nb_scale.set(30)
        self.food_nb_scale.pack(side=TOP)

        Label(self.loc_frames[1], text="Food size :").pack(side=TOP)

        self.food_scale = Scale(self.loc_frames[1], from_=0, to=100, length=100)
        self.food_scale.set(15)
        self.food_scale.pack(side=TOP)

        Label(self.loc_frames[2], text="Queen ants rate(tick) :").pack(side=TOP)

        self.Queen_baby_cd = Scale(self.loc_frames[2], from_=0, to=100, length=100)
        self.Queen_baby_cd.set(20)
        self.Queen_baby_cd.pack(side=TOP)

        Label(self.loc_frames[3], text="Explorer proportion((%) :").pack(side=TOP)

        self.Explorer_prop = Scale(self.loc_frames[3], from_=0, to=100, length=100, command=self.balance_workers)
        self.Explorer_prop.set(70)
        self.Explorer_prop.pack(side=TOP)
 
        Label(self.loc_frames[4], text="Worker proportion((%) :").pack(side=TOP)

        self.Worker_prop = Scale(self.loc_frames[4], from_=0, to=100, length=100, command=self.balance_explorer)
        self.Worker_prop.set(30)
        self.Worker_prop.pack(side=TOP)

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
    model = AntsModel(1,800,600)
    GUI(800,600,model)

import random
import mesa

from Ants import *


class Pheromone:
    def __init__(self):
        self.strength = 0
        self.type = 0


class Nest:
    def __init__(self, queen, members):
        self.queen = queen
        self.members = members
        self.location = self.queen.posi

class AntsModel(mesa.Model):
    """
    Simulate the environment and its ants and nest inside it.
    """
    def __init__(self, nest_nb, width, height):
        self.nest_nb = nest_nb
        self.width = width
        self.height = height
        self.map = [[Pheromone() for x in range(self.width)] for y in range(self.height)]
        self.nest_list = []
        self.schedule = mesa.time.RandomActivation(self)
        self.ids = 0
        for i in range(self.nest_nb):
            self.ids = self.__create_nest(self.ids)

    def __create_nest(self, unique_id):
        nest_id = len(self.nest_list)
        rnd_pos = [random.randint(0, self.width), random.randint(0, self.height)]
        rnd_pos2 = [random.randint(0, self.width), random.randint(0, self.height)]
        agent = Queen(unique_id , self, rnd_pos, nest_id)
        agent_male = Male(unique_id + 1, self, rnd_pos2, nest_id)
        self.schedule.add(agent)
        self.schedule.add(agent_male)
        self.nest_list.append(Nest(agent, [agent_male]))
        return unique_id + 2

    def step(self):
        self.schedule.step()



if __name__ == "__main__":
    model = AntsModel(2, 800,600)
    for iteration in range(10):
        model.step()
        print("Current Ants location : ")
        for ants in model.schedule.agents:
            print(" -> ", ants.posi) 

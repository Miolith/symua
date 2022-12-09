import random
import mesa

from Ants import *


class Pheromone:
    def __init__(self):
        self.strength = 0
        self.type = 0


class Food:
    def __init__(self, serving, pos):
        self.serving = serving
        self.pos = pos
        self.color = "#5ec75a"

class Nest:
    def __init__(self, queen, members):
        self.queen = queen
        self.members = members
        self.location = self.queen.posi
        self.capacity = 10
        self.food_stock = 0


class AntsModel(mesa.Model):
    """
    Simulate the environment and its ants and nest inside it.
    """

    def __init__(self, nest_nb, width, height):
        self.nest_nb = nest_nb
        self.width = width
        self.height = height
        self.map = [[Pheromone() for x in range(self.width)] for y in range(self.height)]
        self.foods_nb = 15
        self.food_max_serving = 15
        self.foods = []
        self.__init_foods()
        self.nest_list = []
        self.schedule = mesa.time.RandomActivation(self)
        self.ids = 0
        for i in range(self.nest_nb):
            self.ids = self.__create_nest(self.ids)

    def find_food(self, x, y):
        for yi in range(-1, 2):
            for xi in range(-1, 2):
                if (not (yi == 0 and xi == 0)) and 0 <= x + xi < self.width and 0 <= y + yi < self.height:
                    if self.map[y + yi][x + xi].strength != 0:
                        return x + xi, y + yi

    def __init_foods(self):
        for food in range(self.foods_nb):
            self.foods.append(Food(random.randint(1, self.food_max_serving),
                                   [random.randint(0, self.width), random.randint(0, self.height)]))

    def food_ticks(self):
        food_total = len(self.foods)
        while food_total < self.foods_nb:
            self.foods.append(Food(random.randint(1, self.food_max_serving),
                                   [random.randint(0, self.width), random.randint(0, self.height)]))

    def __create_nest(self, unique_id):
        nest_id = len(self.nest_list)
        rnd_pos = [random.randint(0, self.width), random.randint(0, self.height)]
        rnd_pos2 = [random.randint(0, self.width), random.randint(0, self.height)]
        agent = Queen(unique_id, self, rnd_pos, nest_id)
        agent_male = Male(unique_id + 1, self, rnd_pos2, nest_id)
        self.schedule.add(agent)
        self.schedule.add(agent_male)
        self.nest_list.append(Nest(agent, [agent_male]))
        return unique_id + 2

    def step(self):
        self.food_ticks()
        self.schedule.step()


if __name__ == "__main__":
    model = AntsModel(2, 800, 600)
    for iteration in range(10):
        model.step()
        print("Current Ants location : ")
        for ants in model.schedule.agents:
            print(" -> ", ants.posi)

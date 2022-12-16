import random
from Stats import *
import mesa

from Ants import *


class Pheromone:
    def __init__(self):
        self.strength = 0
        self.type = 0
        self.source_food_pos = None
        self.tick = 200


class Food:
    def __init__(self, serving, pos):
        self.serving = serving
        self.pos = pos
        self.color = "#5ec75a"

class Nest:
    def __init__(self, queen, members, strat=0):
        self.queen = queen
        self.members = members
        self.alive_soldier = 0
        self.location = self.queen.posi
        self.capacity = 10
        self.strat = strat # 0 : Pacifist, 1 : Defender, 2 : Agressor 3 : Coop
        self.food_stock = 0
        self.dangers = []


class AntsModel(mesa.Model):
    """
    Simulate the environment and its ants and nest inside it.
    """

    def __init__(self, nest_nb, width, height, foods_nb=30, food_max_serving=30):
        self.nest_nb = nest_nb
        self.width = width
        self.height = height
        self.map = [[Pheromone() for x in range(self.width)] for y in range(self.height)]
        self.active_phero = []
        self.foods_nb = foods_nb
        self.food_max_serving = food_max_serving
        self.foods = []
        self.__init_foods()
        self.nest_list = []
        self.schedule = mesa.time.RandomActivation(self)
        self.ids = 0
        self.event_manager = Observer()
        for i in range(self.nest_nb):
            self.event_manager.create_event("nest_population_"+str(i))
            self.event_manager.create_event("soldier_population_" + str(i))
            self.ids = self.__create_nest(self.ids)


    def is_safe(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height


    def yield_queens(self):
        for nest in self.nest_list:
            yield nest.queen

    def find_food(self, x, y, local_nest_id=None):
        for yi in range(-2, 3):
            for xi in range(-2, 3):
                if (not (yi == 0 and xi == 0)) and 0 <= x + xi < self.width and 0 <= y + yi < self.height:
                    obj = self.map[y + yi][x + xi]
                    if obj.strength != 0 and (local_nest_id is None or obj.type == local_nest_id):
                        return obj.source_food_pos
        return None

    def __init_foods(self):
        for food in range(self.foods_nb):
            self.foods.append(Food(random.randint(1, self.food_max_serving),
                                   [random.randint(0, self.width), random.randint(0, self.height)]))

    def food_ticks(self):
        self.foods = list(filter(lambda food:food.serving > 0, self.foods))
        food_total = len(self.foods)
        while food_total < self.foods_nb:
            self.foods.append(Food(random.randint(1, self.food_max_serving),
                                   [random.randint(0, self.width), random.randint(0, self.height)]))
            food_total += 1

    def phero_tick(self):
        for ph in self.active_phero:
            ph.tick -= 1
            if ph.tick <= 0:
                ph.strength = 0
        self.active_phero = list(filter(lambda ph:ph.tick > 0, self.active_phero))

    def nest_tick(self):
        for k,nest in enumerate(self.nest_list):
            nest.dangers = list(filter(lambda target:target.alive == True, nest.dangers))
            if nest.strat == 2 and len(nest.dangers) < 3:
                for i, nest2 in enumerate(self.nest_list):
                    if i == k:
                        continue
                    nb = min(len(nest2.members), 5)
                    for _ in range(nb):
                        nest.dangers.append(random.choice(nest2.members))


        for k,nest in enumerate(self.nest_list):
            nest.members = list(filter(lambda ant:ant.alive == True, nest.members))
            self.event_manager.append_data("nest_population_"+str(k), len(nest.members))
            self.event_manager.append_data("soldier_population_" + str(k), nest.alive_soldier)

    def __create_nest(self, unique_id):
        nest_id = len(self.nest_list)
        rnd_pos = [random.randint(0, self.width), random.randint(0, self.height)]
        rnd_pos2 = [random.randint(0, self.width), random.randint(0, self.height)]
        agent = Queen(unique_id, self, rnd_pos, nest_id)
        agent_male = Male(unique_id + 1, self, rnd_pos2, nest_id)
        self.schedule.add(agent)
        self.schedule.add(agent_male)
        self.nest_list.append(Nest(agent, [agent_male]))
        self.event_manager.append_data("nest_population_"+str(nest_id), 1)
        self.event_manager.append_data("soldier_population_" + str(nest_id), 0)
        return unique_id + 2

    def step(self):
        self.phero_tick()
        self.food_ticks()
        self.nest_tick()
        self.schedule.step()


if __name__ == "__main__":
    model = AntsModel(1, 800, 600)
    for iteration in range(10):
        model.step()
        print("Current Ants location : ")
        for ants in model.schedule.agents:
            print(" -> ", ants.posi)

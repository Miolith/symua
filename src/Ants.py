import mesa
import random

class Ants(mesa.Agent):
    def __init__(self, unique_id, model, position, nest_id):
        super().__init__(unique_id, model)
        self.posi = position
        self.nest_id = nest_id
        self.movespeed = 1
        self.color = "green"
        self.trace = 0
        self.alive = True

    def distance_to_target(self, target_x, target_y):
        return (self.posi[0] - target_x)**2 + (self.posi[1] - target_y)**2 


    def move_towards(self, goal_x, goal_y, min_dist, max_dist):
        leap = random.uniform(min_dist, max_dist)
        direction_y = (goal_y - self.posi[1])
        direction_x = (goal_x - self.posi[0])
        self.posi[0] += direction_x * leap
        self.posi[1] += direction_y * leap

    def step(self):
        if not self.alive:
            return
        mx = random.uniform(-5,5)
        my = random.uniform(-5,5)
        if 0 <= self.posi[0] + mx < self.model.width and 0 <= self.posi[1] + my < self.model.height:
            self.posi[0] += mx
            self.posi[1] += my
            #self.model.map[int(self.posi[1])][int(self.posi[0])].strength += self.trace
        

class Queen(Ants):
    def __init__(self, unique_id, model, position, nest_id):
        super().__init__(unique_id, model, position, nest_id)
        self.color = "#B715FE"
        self.hasReproduced = False
        self.antsSpawnRate = 10
        self.tick = 0


    def step(self):
        if not self.alive:
            return
        self.tick += 1
        if self.hasReproduced:
            if self.tick >= self.antsSpawnRate:
                baby = Ants(self.model.ids, self.model, list(self.posi), self.nest_id)
                self.model.schedule.add(baby)
                self.model.ids += 1
                self.tick = 0


class Male(Ants):
    def __init__(self, unique_id, model, position, nest_id):
        super().__init__(unique_id, model, position, nest_id)
        self.color = "blue"

    def step(self):
        if not self.alive:
            return

        queen_pos = self.model.nest_list[self.nest_id].location
        if self.distance_to_target(queen_pos[0], queen_pos[1]) > 2:
            self.move_towards(queen_pos[0], queen_pos[1], 0, self.movespeed)
        else:
            self.model.nest_list[self.nest_id].queen.hasReproduced = True
            self.alive = False
            self.model.schedule.remove(self)


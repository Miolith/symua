import random
import mesa

PREDATOR_LIFETIME = 100
PREDATOR_ATTACK = 30

class Predator(mesa.Agent):
    def __init__(self, unique_id, model, position):
        super().__init__(unique_id, model)
        self.posi = position
        self.movespeed = 2
        self.color = "pink"
        self.lifetime = PREDATOR_LIFETIME
        self.alive = True

    def distance_to_target(self, target_x, target_y):
        return (self.posi[0] - target_x) ** 2 + (self.posi[1] - target_y) ** 2

    def move_towards(self, goal_x, goal_y, min_dist, max_dist):
        direction_y = (goal_y - self.posi[1])
        direction_x = (goal_x - self.posi[0])
        leap = random.uniform(min_dist, max_dist)
        leap = min(abs(direction_x) + abs(direction_y), leap)
        self.posi[0] += direction_x * leap
        self.posi[1] += direction_y * leap


    def random_move(self):
        mx = random.uniform(-5, 5)
        my = random.uniform(-5, 5)
        if 0 <= self.posi[0] + mx < self.model.width and 0 <= self.posi[1] + my < self.model.height:
            self.posi[0] += mx
            self.posi[1] += my

    def step(self):
        if not self.alive:
            return
        self.move_and_kill()
        if self.lifetime < 0:
            self.alive = False

    # TO OPTIMIZE
    def move_and_kill(self):
        if not self.alive:
            return
        closest_ant = None
        closest_dist = 1000
        for ant in self.model.schedule.agents:
            if ant.alive:
                dist = self.distance_to_target(ant.posi[0], ant.posi[1])
                if dist < closest_dist:
                    closest_dist = dist
                    closest_ant = ant
        if closest_dist < 5:
            self.move_towards(closest_ant.posi[0], closest_ant.posi[1], 0, self.movespeed)
            closest_ant.lifetime -= PREDATOR_ATTACK
            if closest_ant.lifetime < 0:
                 closest_ant.alive = False
        else:
            self.random_move()

import mesa
import random

ANT_LIFETIME = 50
SOLDIER_ANT_ATTACK = 10

REFILL_TRESHOLD = 30

class Ants(mesa.Agent):
    def __init__(self, unique_id, model, position, nest_id):
        super().__init__(unique_id, model)
        self.posi = position
        self.nest_id = nest_id
        self.movespeed = 1
        self.color = "green"
        self.trace = 0
        self.alive = True
        self.lifetime = ANT_LIFETIME
        self.food_effect = 40

    def distance_to_target(self, target_x, target_y):
        return (self.posi[0] - target_x)**2 + (self.posi[1] - target_y)**2 

    def move_towards(self, goal_x, goal_y, min_dist, max_dist):
        direction_y = (goal_y - self.posi[1])
        direction_x = (goal_x - self.posi[0])
        leap = random.uniform(min_dist, max_dist)
        leap = min(abs(direction_x) + abs(direction_y), leap)
        self.posi[0] += direction_x * leap
        self.posi[1] += direction_y * leap

    def refill_at_nest(self):
        location = self.model.nest_list[self.nest_id].location
        if self.distance_to_target(location[0], location[1]) > 2:
            self.move_towards(location[0], location[0], 0, self.movespeed)
        elif self.model.nest_list[self.nest_id].food_stock > 0:
            self.model.nest_list[self.nest_id].food_stock -= 1
            self.lifetime += self.food_effect

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
                self.model.nest_list[self.nest_id].members.append(baby)
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

class Explorer(Ants):
    def __init__(self, unique_id, model, position, nest_id):
        super().__init__(unique_id, model, position, nest_id)
        self.color = "yellow"
        self.carryFood = False
        self.target = None
        self.foodQte = 0

    def go_back_home(self):
        location = self.model.nest_list[self.nest_id].location
        if self.distance_to_target(location[0], location[1]) > 2:
            self.move_towards(location[0], location[0], 0, self.movespeed)
        elif self.carryFood:
            if self.foodQte > 1 and self.lifetime <= REFILL_TRESHOLD:
                self.lifetime += self.food_effect
                self.foodQte -= 1
            self.model.nest_list[self.nest_id].food_stock += self.foodQte
            self.foodQte = 0
            self.carryFood = False
            self.trace = 0
        else:
            self.trace = 0

    def step(self):
        if not self.alive:
            return
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False
            self.model.schedule.remove(self)
        elif self.lifetime <= REFILL_TRESHOLD:
            self.refill_at_nest()
        else:
            # TO OPTIMIZE
            if not self.trace:
                for food in self.model.foods:
                    if food.pos == self.posi:
                        self.trace = 1

                if self.target is None or self.posi == self.target:
                    self.target = [random.randint(0, self.model.width), random.randint(0, self.model.height)]

                self.move_towards(self.target[0], self.target[1], 0, self.movespeed)
            else:
                self.go_back_home()
                self.model.map[int(self.posi[1])][int(self.posi[0])].strength += self.trace


# TO OPTIMIZE
class Soldier(Ants):
    def __init__(self, unique_id, model, position, nest_id):
        super().__init__(unique_id, model, position, nest_id)
        self.color = "green"
        self.model.nest_list[self.nest_id].capacity += 10

    def step(self):
        if not self.alive:
            return
        self.chase_predator()
        self.lifetime -= 1
        if self.lifetime < 0:
            self.alive = False
            self.model.schedule.remove(self)

    def chase_predator(self):
        closest_predator = None
        closest_dist = 1000
        for predator in self.model.schedule.predators:
            if predator.alive:
                dist = self.distance_to_target(predator.posi[0], predator.posi[1])
                if dist < closest_dist:
                    closest_dist = dist
                    closest_predator = predator
        if closest_dist < 5:
            self.move_towards(closest_predator.posi[0], closest_predator.posi[1], 0, self.movespeed)
            closest_predator.lifetime -= SOLDIER_ANT_ATTACK
            if closest_predator.lifetime < 0:
                 closest_predator.alive = False
        else:
            self.chase_the_closest_explorer()

    def chase_the_closest_explorer(self):
        closest_explorer = None
        closest_dist = 1000
        for ant in self.model.nest_list[self.nest_id].members:
            if isinstance(ant, Explorer):
                if ant.alive:
                    dist = self.distance_to_target(ant.posi[0], ant.posi[1])
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_explorer = ant
        if closest_dist < 5:
            self.move_towards(closest_explorer.posi[0], closest_explorer.posi[1], 0, self.movespeed)


class Worker(Ants):
    def __init__(self, unique_id, model, position, nest_id):
        super().__init__(unique_id, model, position, nest_id)
        self.color = "red"
        self.target = None
        self.wandering_range = 5
        
    def step(self):
        if not self.alive:
            return
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False
            self.model.schedule.remove(self)
        elif self.lifetime <= REFILL_TRESHOLD:
            self.refill_at_nest()
        else:
            if self.model.map[int(self.posi[1])][int(self.posi[0])].strength > 0:
                food_pos = self.model.find_food(self.posi[1],self.posi[0])
                self.move_towards(food_pos[0], food_pos[1], 0, self.movespeed)
            else:
                if self.target is None or self.posi == self.target:
                    nest_loc = self.model.nest_list[self.nest_id].location
                    self.target = [nest_loc[0] + random.uniform(-self.wandering_range, self.wandering_range),
                                   nest_loc[1] + random.uniform(-self.wandering_range, self.wandering_range)]

                self.move_towards(self.target[0], self.target[1], 0, self.movespeed)
    


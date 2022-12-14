import mesa
import random
import math

ANT_LIFETIME = 50
SOLDIER_ANT_ATTACK = 20

DEFAULT_PHERO_TICK = 200

REFILL_TRESHOLD = 30

class Ants(mesa.Agent):
    def __init__(self, unique_id, model, position, nest_id):
        super().__init__(unique_id, model)
        self.posi = position
        self.nest_id = nest_id
        self.movespeed = 5
        self.color = "green"
        self.trace = 0
        self.alive = True
        self.lifetime = ANT_LIFETIME
        self.food_effect = 40
        self.lifetime_rate = 0.25
        self.nest_location = None
        if nest_id < len(self.model.nest_list):
            self.nest_location = self.model.nest_list[nest_id].location
    def distance_to_target(self, target_x, target_y):
        return (self.posi[0] - target_x)**2 + (self.posi[1] - target_y)**2 

    def move_towards(self, goal_x, goal_y, max_dist, dist_to_target=None):
        
        if dist_to_target is None:
            dist_to_target = self.distance_to_target(goal_x, goal_y)
        dist_to_target = math.sqrt(dist_to_target)
        if dist_to_target <= max_dist or dist_to_target == 0:
            self.posi[0] = goal_x
            self.posi[1] = goal_y
            return
        
        direction_y = (goal_y - self.posi[1])
        direction_x = (goal_x - self.posi[0])
        self.posi[0] += (direction_x / dist_to_target) * max_dist
        self.posi[1] += (direction_y / dist_to_target) * max_dist

    def refill_at_nest(self):
        dist = self.distance_to_target(self.nest_location[0], self.nest_location[1])
        if dist > 2:
            self.move_towards(self.nest_location[0], self.nest_location[1], self.movespeed, dist)
        elif self.model.nest_list[self.nest_id].food_stock > 0:
            self.model.nest_list[self.nest_id].food_stock -= 1
            self.lifetime += self.food_effect

    def get_attacked(self, amount_hp_lost, attacker):
        self.lifetime -= amount_hp_lost

        # Notify Nest that Unit is attacked
        personal_nest = self.model.nest_list[self.nest_id]
        if personal_nest.strat != 3:
            danger_list = personal_nest.dangers
            if attacker not in danger_list:
                danger_list.append(attacker)
        else:
            for lnest in self.model.nest_list:
                if lnest.strat == 3:
                    danger_list = lnest.dangers
                    if attacker not in danger_list:
                        danger_list.append(attacker)
    def step(self):
        if not self.alive:
            return

        self.lifetime -= self.lifetime_rate
        if self.lifetime <= 0:
            self.alive = False
            self.model.schedule.remove(self)
            return

        mx = random.uniform(-5,5)
        my = random.uniform(-5,5)
        if 0 <= self.posi[0] + mx < self.model.width and 0 <= self.posi[1] + my < self.model.height:
            self.posi[0] += mx
            self.posi[1] += my
            #self.model.map[int(self.posi[1])][int(self.posi[0])].strength += self.trace
        

class Queen(Ants):
    def __init__(self, unique_id, model, position, nest_id, strat=0):
        super().__init__(unique_id, model, position, nest_id)
        self.color = "#B715FE"
        self.hasReproduced = False
        self.antsSpawnRate = 20
        self.explorer_chance = 0.7
        self.worker = 0.3
        self.soldier_chance = 0
        self.strat = strat
        self.tick = 200
        self.baby_types = [Explorer, Worker]
        self.nest = None
        self.baby_burst = 10
        self.food_greed = 1
        #self.lifetime_rate /= 2
    def can_make_baby(self):
        if self.nest is None:
            self.nest = self.model.nest_list[self.nest_id]
        if self.baby_burst > 0:
            self.baby_burst -= 1
            self.nest.food_stock += 2
            return True
        if len(self.nest.members)*self.food_greed < self.nest.food_stock:
            return True
        return False

    def select_type(self):
        value = random.uniform(0,1)
        if value < self.explorer_chance:
            return Explorer
        else:
            if self.strat > 0:
                if random.uniform(0,1) < self.soldier_chance:
                    self.model.nest_list[self.nest_id].alive_soldier += 1
                    return Soldier
            return Worker

    def step(self):
        if not self.alive:
            return
        self.tick += 1
        #self.lifetime -= self.lifetime_rate
        if self.hasReproduced:
            if self.tick >= self.antsSpawnRate and self.can_make_baby():
                b_types = self.select_type()
                baby = b_types(self.model.ids, self.model, list(self.posi), self.nest_id)
                self.nest.members.append(baby)
                self.model.schedule.add(baby)
                self.model.ids += 1
                self.tick = 0
                self.nest.food_stock -= 1
        #if self.lifetime <= REFILL_TRESHOLD:
        #    if self.model.nest_list[self.nest_id].food_stock > 0:
        #        self.model.nest_list[self.nest_id].food_stock -= 1
        #        self.lifetime += self.food_effect


class Male(Ants):
    def __init__(self, unique_id, model, position, nest_id):
        super().__init__(unique_id, model, position, nest_id)
        self.color = "blue"

    def step(self):
        if not self.alive:
            return
        queen_pos = self.model.nest_list[self.nest_id].location
        dist = self.distance_to_target(queen_pos[0], queen_pos[1])
        if dist > 2:
            self.move_towards(queen_pos[0], queen_pos[1], self.movespeed, dist)
        else:
            self.model.nest_list[self.nest_id].queen.hasReproduced = True
            self.alive = False
            self.model.schedule.remove(self)

class Explorer(Ants):
    def __init__(self, unique_id, model, position, nest_id):
        super().__init__(unique_id, model, position, nest_id)
        self.color = "#9a9c3a"
        self.carryFood = False
        self.savedFoodPos = None
        self.target = None
        self.foodQte = 0
        self.movespeed = 5
        self.max_food_capacity = 3
    def go_back_home(self):
        dist = self.distance_to_target(self.nest_location[0], self.nest_location[1])
        if dist > 2:
            self.move_towards(self.nest_location[0], self.nest_location[1], self.movespeed, dist)
        elif self.carryFood:
            if self.foodQte > 1 and self.lifetime <= REFILL_TRESHOLD:
                self.lifetime += self.food_effect
                self.foodQte -= 1
            self.model.nest_list[self.nest_id].food_stock += self.foodQte
            self.foodQte = 0
            self.carryFood = False
            self.trace = 0
            self.color = "#9a9c3a"
        else:
            if self.lifetime <= REFILL_TRESHOLD and self.model.nest_list[self.nest_id].food_stock > 0:
                self.model.nest_list[self.nest_id].food_stock -= 1
                self.lifetime += self.food_effect
            self.trace = 0

    def track_food(self):
        for food in self.model.foods:
            dist_to_food = self.distance_to_target(*food.pos)
            if dist_to_food <= 15:
                self.trace = 1
                self.savedFoodPos = food.pos
                if food.serving > 0:
                    self.color = "#ffb366"
                    self.carryFood = True
                    self.foodQte = min(food.serving, self.max_food_capacity)
                    food.serving -= self.foodQte
            elif dist_to_food <= 200:
                self.target = food.pos

    def step(self):
        if not self.alive:
            return
        self.lifetime -= self.lifetime_rate
        if self.lifetime <= 0:
            self.alive = False
            self.model.schedule.remove(self)
        elif self.lifetime <= REFILL_TRESHOLD:
            self.go_back_home()
            if self.trace:
                phero = self.model.map[int(self.posi[1])][int(self.posi[0])]
                phero.strength += self.trace
                phero.tick = DEFAULT_PHERO_TICK
                phero.type = self.nest_id
                phero.source_food_pos = self.savedFoodPos
                self.model.active_phero.append(phero)
        else:
            # TO OPTIMIZE
            if not self.trace:
                self.track_food()
                dist = 0
                if self.target is not None:
                    dist = self.distance_to_target(*self.target)
                if self.target is None or dist <= 2:
                    self.target = [random.randint(0, self.model.width), random.randint(0, self.model.height)]
                    dist = self.distance_to_target(*self.target)
                self.move_towards(self.target[0], self.target[1], self.movespeed, dist)

            else:
                self.go_back_home()
                phero = self.model.map[int(self.posi[1])][int(self.posi[0])]
                phero.strength += self.trace
                phero.tick = DEFAULT_PHERO_TICK
                phero.type = self.nest_id
                phero.source_food_pos = self.savedFoodPos
                self.model.active_phero.append(phero)

# TO OPTIMIZE
class Soldier(Ants):
    def __init__(self, unique_id, model, position, nest_id, soldier_damage=SOLDIER_ANT_ATTACK):
        super().__init__(unique_id, model, position, nest_id)
        self.color = "green"
        self.nest = self.model.nest_list[nest_id]
        self.target = None
        self.target_obj = None
        self.dmg = soldier_damage
        self.wandering_range = 200
        self.speed_rush_value = 5
        self.speed_rush_cd = 30
        self.speed_rush_duration = 10
        self.effect_on = False
        self.cd = random.randint(0,self.speed_rush_cd+1)

    def go_back_home(self):
        dist = self.distance_to_target(self.nest_location[0], self.nest_location[1])
        if dist > 2:
            self.move_towards(self.nest_location[0], self.nest_location[1], self.movespeed, dist)
        else:
            if self.lifetime <= REFILL_TRESHOLD and self.model.nest_list[self.nest_id].food_stock > 0:
                self.model.nest_list[self.nest_id].food_stock -= 1
                self.lifetime += self.food_effect

    def find_target(self):
        if len(self.nest.dangers) > 0:
            self.target_obj = random.choice(self.nest.dangers)
            self.target = self.target_obj.posi
        else:
            self.target = None
            self.target_obj = None

    def valid_pos_around_nest(self):
         self.target = [self.nest_location[0] + random.uniform(-self.wandering_range, self.wandering_range),
                            self.nest_location[1] + random.uniform(-self.wandering_range, self.wandering_range)]
         while not self.model.is_safe(*self.target):
             self.target = [self.nest_location[0] + random.uniform(-self.wandering_range, self.wandering_range),
                            self.nest_location[1] + random.uniform(-self.wandering_range, self.wandering_range)]

    def speed_rush(self):
        if self.cd >= self.speed_rush_cd:
            self.cd = 0
            self.movespeed += self.speed_rush_value
            self.effect_on = True

    def step(self):
        if not self.alive:
            return

        self.cd += 1
        if self.effect_on and self.cd >= self.speed_rush_duration:
            self.effect_on = False
            self.movespeed -= self.speed_rush_value

        self.lifetime -= self.lifetime_rate
        if self.lifetime < 0:
            self.alive = False
            self.model.schedule.remove(self)
            self.model.nest_list[self.nest_id].alive_soldier -= 1
            return
        elif self.lifetime <= REFILL_TRESHOLD:
            self.go_back_home()
            self.target = None
            self.target_obj = None
        else:
            if self.target_obj is None:
                self.find_target()

            if self.target is None:
                dist = 0
                if self.target is not None:
                    dist = self.distance_to_target(*self.target)
                if self.target is None:
                    self.valid_pos_around_nest()
                    dist = self.distance_to_target(*self.target)
                self.move_towards(self.target[0], self.target[1], self.movespeed, dist)
            else:
                dist = self.distance_to_target(*self.target)
                if dist > 2:
                    self.speed_rush()
                    self.move_towards(self.target[0], self.target[1], self.movespeed, dist)
                elif self.target_obj is not None: # Attack
                    self.target_obj.get_attacked(self.dmg, self)
                    if not self.target_obj.alive:
                        self.target = None
                        self.target_obj = None
                        self.lifetime += self.food_effect
                else:
                    self.target = None


class Worker(Ants):
    def __init__(self, unique_id, model, position, nest_id):
        super().__init__(unique_id, model, position, nest_id)
        self.color = "red"
        self.target = None
        self.wandering_range = 50
        self.carryFood = False
        self.savedFoodPos = None
        self.foodQte = 0
        self.trace = 0
        self.max_food_capacity = 7
    
    def track_food(self):
        for food in self.model.foods:
            dist_to_food = self.distance_to_target(*food.pos)
            if dist_to_food <= 15:
                self.trace = 1
                self.savedFoodPos = food.pos
                if food.serving > 0:
                    self.color = "#ffb366"
                    self.carryFood = True
                    self.foodQte = min(food.serving, self.max_food_capacity)
                    food.serving -= self.foodQte
            elif dist_to_food <= 200:
                self.target = food.pos
    
    def go_back_home(self):
        dist = self.distance_to_target(self.nest_location[0], self.nest_location[1])
        if dist > 2:
            self.move_towards(self.nest_location[0], self.nest_location[1], self.movespeed, dist)
        elif self.carryFood:
            if self.foodQte > 1 and self.lifetime <= REFILL_TRESHOLD:
                self.lifetime += self.food_effect
                self.foodQte -= 1
            self.model.nest_list[self.nest_id].food_stock += self.foodQte
            self.foodQte = 0
            self.carryFood = False
            self.foundfood = False
            self.trace = 0
            self.color = "red"
        else:
            if self.lifetime <= REFILL_TRESHOLD and self.model.nest_list[self.nest_id].food_stock > 0:
                self.model.nest_list[self.nest_id].food_stock -= 1
                self.lifetime += self.food_effect
            self.trace = 0
            self.foundfood = False

    def notify_food_supply_ended(self):
        dist = self.distance_to_target(self.nest_location[0], self.nest_location[1])
        if dist > 2:
            self.move_towards(self.nest_location[0], self.nest_location[1], self.movespeed, dist)
        else:
            if self.lifetime <= REFILL_TRESHOLD and self.model.nest_list[self.nest_id].food_stock > 0:
                self.model.nest_list[self.nest_id].food_stock -= 1
                self.lifetime += self.food_effect
            self.trace = 0

    def step(self):
        if not self.alive:
            return
        self.lifetime -= self.lifetime_rate
        if self.lifetime <= 0:
            self.alive = False
            self.model.schedule.remove(self)
        elif self.trace == -1:
            phero = self.model.map[int(self.posi[1])][int(self.posi[0])]
            if phero.strength > 0:
                phero.strength = 0
                phero.tick = 0
                phero.type = -1

            self.go_back_home()
        elif self.lifetime <= REFILL_TRESHOLD:
            self.go_back_home()
            if not self.trace:
                phero = self.model.map[int(self.posi[1])][int(self.posi[0])]
                phero.strength += self.trace
                phero.tick = DEFAULT_PHERO_TICK
                phero.type = self.nest_id
                phero.source_food_pos = self.savedFoodPos
                self.model.active_phero.append(phero)
        elif self.trace:
            self.go_back_home()
            phero = self.model.map[int(self.posi[1])][int(self.posi[0])]
            phero.strength += self.trace
            phero.tick = DEFAULT_PHERO_TICK
            phero.type = self.nest_id
            phero.source_food_pos = self.savedFoodPos
            self.model.active_phero.append(phero)
        else:
            if self.target is None or self.target == self.posi:
                int_pos = (int(self.posi[0]),int(self.posi[1]))
                food_pos = self.model.find_food(*int_pos, self.nest_id)
                if food_pos is not None:
                    self.target = food_pos
                    self.foundfood = True
                else:
                    self.foundfood = False
                    self.target = [self.nest_location[0] + random.uniform(-self.wandering_range, self.wandering_range),
                                    self.nest_location[1] + random.uniform(-self.wandering_range, self.wandering_range)]
                    while not self.model.is_safe(*self.target):
                        self.target = [self.nest_location[0] + random.uniform(-self.wandering_range, self.wandering_range),
                                    self.nest_location[1] + random.uniform(-self.wandering_range, self.wandering_range)]

            dist = self.distance_to_target(self.target[0], self.target[1])
            if dist > 2:
                self.move_towards(self.target[0], self.target[1], self.movespeed, dist)
                self.track_food()
            elif self.foundfood:
                self.track_food()
                if not self.trace:
                    self.trace = -1
            else:
                self.target = None

            if not self.foundfood:
                int_pos = (int(self.posi[0]), int(self.posi[1]))
                food_pos = self.model.find_food(*int_pos, self.nest_id)
                if food_pos is not None:
                    self.target = food_pos
                    self.foundfood = True



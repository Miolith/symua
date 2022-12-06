import mesa
import random

class ExempleAgent(mesa.Agent):
    """
    An Exemple agent representing a player in gambling.
    The following stats are used to represent our agent :
        - base_amount : his initial amount of money 
        - loose_tolerance : the number of consecutive lost after he stop
          playing
        - safety : How safe the agent will bet (% of his money)
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.base_amount = random.randint(100,10000)
        self.loose_tolerance = random.randint(2,30)
        self.safety = random.uniform(0.2,1)
        self.loose_count = 0
        self.isPlaying = True
    def step(self):
        if self.isPlaying:
            bet = random.uniform(0.01, self.safety) * self.base_amount
            self.base_amount -= bet
            if self.model.Play(bet):
                self.base_amount += 2*bet
                self.loose_count = 0
            else:
                self.loose_count += 1
            if self.loose_count > self.loose_tolerance:
                self.isPlaying = False
        



class ExempleModel(mesa.Model):
    """A model representing a casino/scam trying to make profit out of agents"""

    def __init__(self, N, win_rate, lose_step, win_step, min_winrate,
            max_winrate):
        self.win_rate = win_rate
        self.win_step = win_step
        self.loose_step = lose_step
        self.mx_wr = max_winrate
        self.mi_wr = min_winrate
        self.num_agents = N
        self.schedule = mesa.time.RandomActivation(self)
        self.baseMoney = 100000
        self.currentMoney = self.baseMoney
        # Create agents
        for i in range(self.num_agents):
            a = ExempleAgent(i, self)
            self.schedule.add(a)

    def Play(self, amount):
        self.currentMoney += amount
        win = random.uniform(0,1) <= self.win_rate
        if win:
            self.win_rate *= self.win_step
        else:
            self.win_rate *= self.loose_step
            self.currentMoney -= 2*amount
        if self.win_rate > self.mx_wr:
            self.win_rate = self.mx_wr
        elif self.win_rate <  self.mi_wr:
            self.win_rate = self.mi_wr
        if self.currentMoney < 0:
            self.currentMoney = 0
        return win

    def step(self):
        self.schedule.step()

if __name__ == "__main__":
    model = ExempleModel(100, 0.6, 0.99,1.25, 0.00001, 0.75)
    for iteration in range(10):
        model.step()
        print("Current Model W/R at ", model.win_rate)
        print("Current Model money : ", model.currentMoney)
        print("Current Model % Gain : ", ((model.currentMoney
            / model.baseMoney) - 1) * 100)
        print("Number of active users : ", sum(int(e.isPlaying) for e in
            model.schedule.agents))

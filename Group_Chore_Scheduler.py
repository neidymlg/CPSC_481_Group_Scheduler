import random
import math
from typing import List, Dict, Tuple
import copy

import numpy as np
class Chore:
    name: str
    amount: int

    def __init__(self, name, amount):
        self.name = name
        self.amount = amount
    
class User:
    max_chores: int
    name: str

    def __init__(self, name, max_chores):
        self.name = name
        self.max_chores = max_chores
        

class Chore_Scheduler:
    def __init__(self, chores: List[Chore], users: List[User]):
        self.chores = chores
        #rearranges users so users with more chore capacity will get more chores when calling create_initial_schedule 
        self.users = sorted(users, key=lambda x: x.max_chores, reverse=True) 
        self.total_chores = sum(chore.amount for chore in self.chores)
        self.schedule = self.create_initial_schedule()

    def create_initial_schedule(self) -> Dict[str, List[str]]:
            schedule = {user.name: [] for user in self.users}
            user_amount = len(self.users)

            #gets all chore names, gets all chore amount
            #repeats chores (Ex: (Dishes, 2) -> [Dishes, Dishes])
            chore_names = np.array([chore.name for chore in self.chores], dtype=object)
            chore_amounts = np.array([chore.amount for chore in self.chores], dtype=int)
            repeated_chore_list = np.repeat(chore_names, chore_amounts)  

            #distributes chores to be half and half (or approximately)
            for i, chore_name in enumerate(repeated_chore_list):
                user = self.users[i % user_amount]
                schedule[user.name].append(chore_name)

            return schedule


    def jains_fairness_index(values: List):
        n = len(values)
        numerator = np.sum(values) ** 2
        denominator = n * np.sum(values ** 2)
        return numerator / denominator


    def evaluation_function(self, schedule):
        score = 100
        user_info = {user.name: user for user in self.users}
        ratios = []
        penalty - 0

        for user_name, chores in schedule.items():
            num_chores = len(chores)
            max_chores = user_info[user_name].max_chores
            ratios.append(num_chores/max_chores)
        
        np.mean(chore_ratio)
        # for chore_name, person_name in schedule.items():
        #     user_copy[person_name] += 1

        # get the amount of chores a user can do and check if there is 
        # more than usual over everywhere (unless everyone is overloaded),
        # if less than usual it's okay, if no one is overloaded except one penalize
        # decrease score if overloaded, increase score if not overloaded
        raise NotImplementedError
        

    def get_neighbors(self, schedule: Dict[str, List[str]], num_swaps):
        neighbors = []
        user_names = list(schedule.keys())

        for _ in range(num_swaps):
            schedule_copy = copy.deepcopy(schedule)
            strategy = random.choice(['reassign', 'swap'])
            user_1, user_2 = random.sample(user_names, 2)


            if strategy == 'reassign' and len(schedule_copy[user_1]) > 0:
                chore_i = random.randint(0, len(schedule_copy[user_1]) - 1)
                chore = schedule_copy[user_1].pop(chore_i)
                schedule_copy[user_2].append(chore)
            else:
                id_1 = random.randint(0, len(schedule_copy[user_1]) - 1)
                id_2 = random.randint(0, len(schedule_copy[user_2]) - 1)
                schedule_copy[user_1][id_1], schedule_copy[user_2][id_2] = schedule_copy[user_2][id_2], schedule_copy[user_1][id_1]

            neighbors.append(schedule_copy)
        return neighbors

    
    def simulated_annealing(self, max_iterations: int = 1000, initial_temp: float = 100.0, cooling_rate: float = 0.95):
        current_schedule = {k: v.copy() for k, v in self.schedule.items()}
        current_score = self.evaluation_function(current_schedule)

        best_schedule = current_schedule
        best_score = current_score
        
        temp = initial_temp

        for i in range(max_iterations):
            neighbors = self.get_neighbors(current_schedule, (self.total_chores * 2))
            evaluation_scores = []

            neighbor_id = random.randint(0, len(neighbors) - 1)
            neighbor_schedule = neighbors.pop(neighbor_id)
            neighbor_score = evaluation_scores(neighbor_schedule)

            delta = neighbor_score - current_score
            if delta > 0:
                current_schedule =  neighbor_schedule
                current_score = neighbor_score
            else:
                #possible bad choice
                acceptance_probability = 0
                if temp > 0:
                    acceptance_probability = math.exp(delta/temp)
                if random.random() < acceptance_probability:
                    current_schedule =  neighbor_schedule
                    current_score = neighbor_score
                #else no change to current schedule

        if current_score < best_score:
            best_schedule = current_schedule
            best_score = best_score
        
        temp *= cooling_rate

        return best_schedule, best_score
                


if __name__ == "__main__":

    chore_list = list([Chore("dishes", 3), Chore("cooking", 4), Chore("trash", 1), Chore("mopping", 2)])
    user_list = list([User("User_1", max_chores=2), User("User_2", max_chores=8)])
    cs = Chore_Scheduler(chore_list, user_list)
    # user_info = [
    #     {'name': 'User_1', 'maximum_chores': 5, 'difficulty': [0, 4, 2, 0], 'hated_chores':['cooking'], 'preferred_chores':['dishes']},
    #     {'name': 'User_2', 'maximum_chores': 5, 'difficulty': [1, 1, 0, 1], 'hated_chores':['trash'], 'preferred_chores':['cooking']}
    # ]
    # chores = [
    #     {"dishes": 3},
    #     {"cooking": 4},
    #     {"trash": 1},
    #     {"mopping": 2}
    # ]
    # max_chores = 10
    # cs = Chore_Scheduler(user_info=user_info, chores=chores, max_chores=max_chores)


    
import random
import math
from typing import List, Dict, Tuple
import copy

import numpy as np
class Chore:
    def __init__(self, name: str, amount: int):
        self.name = name
        self.amount = amount
    
class User:
    def __init__(self, name: str, max_chores: int, 
                difficulty: List[int] = None, 
                hated_chores: List[int] = None,
                loved_chores: List[int] = None):
        self.name = name
        self.max_chores = max_chores
        self.difficulty = difficulty
        self.hated_chores = hated_chores
        self.loved_chores = loved_chores
        
def jains_divide(numerator, denominator):
        if denominator == 0:
            return 1.0
        return numerator/denominator

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

    def jains_fairness_index(self, values: np.ndarray) -> float:
        n = len(values)
        numerator = np.sum(values) ** 2
        denominator = n * np.sum(values ** 2)
        return jains_divide(numerator, denominator)

    def evaluation_function(self, schedule):
        user_info = {user.name: user for user in self.users}

        # --------------Chore Capacity and Fairness of Distribution-------------
        user_names = list(schedule.keys())
        chore_counts = np.array([len(schedule[name]) for name in user_names])
        user_max_chores = np.array([user_info[name].max_chores for name in user_names])
        ratios = chore_counts / user_max_chores
        fairness_score = self.jains_fairness_index(ratios)
        score = fairness_score * 100.0

        overload_mask = ratios > 1.0
        overload_count = np.sum(overload_mask)

        #penalty if only some are overloaded 
        if overload_count > 0:
            if overload_count == len(ratios) and fairness_score > 0.90:
                decimal_score = ((fairness_score*100)%10)
                if decimal_score < 1:
                    decimal_score = 10
                score += min(decimal_score, 10)
            else:
                worst_overload = np.max(ratios[overload_mask])
                score -= min(worst_overload * 3, 10)
        else:
            score += min(fairness_score*10,10)

        # for user_name in user_names:
        #     # --------------User Preference-------------
        #     user = user_info[user_name]
        #     assigned_chores = schedule[user_name]
        #     assigned_iid = [self.chore_name]
        #     # --------------Individual Difficulty-------------


        return score
        

    def get_neighbors(self, schedule: Dict[str, List[str]], num_swaps):
        neighbors = []
        user_names = list(schedule.keys())

        for _ in range(num_swaps):
            schedule_copy = copy.deepcopy(schedule)
            strategy = random.choice(['reassign', 'swap'])
            strategy = 'reassign'
            user_1, user_2 = random.sample(user_names, 2)


            if strategy == 'reassign' and len(schedule_copy[user_1]) > 1:
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
        current_schedule = copy.deepcopy(self.schedule)
        current_score = self.evaluation_function(current_schedule)

        best_schedule = current_schedule
        best_score = current_score
        
        temp = initial_temp

        for i in range(max_iterations):
            num_neighbors = min(self.total_chores * 2, 20)
            neighbors = self.get_neighbors(current_schedule, num_neighbors)
            neighbor_id = random.randint(0, len(neighbors) - 1)
            neighbor_schedule = neighbors.pop(neighbor_id)
            neighbor_score = self.evaluation_function(neighbor_schedule)

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
                #no change to current schedule happened

            if current_score > best_score:
                best_schedule = current_schedule
                best_score = current_score
            
            temp *= cooling_rate

        return best_schedule, best_score
                


if __name__ == "__main__":

    chore_list = list([Chore("dishes", 3), Chore("cooking", 4), Chore("trash", 1), Chore("mopping", 2)])
    user_list = list([User("User_1", max_chores=5, difficulty = [0,0,0,0], hated_chores=[1,2], loved_chores=[0,3]), User("User_2", max_chores=5, hated_chores=[], loved_chores=[0,1])])
    cs = Chore_Scheduler(chore_list, user_list)
    schedule, score = cs.simulated_annealing()
    print(f"{schedule=}")
    print(f"{score=}")
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


    
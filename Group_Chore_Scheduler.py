import random
import math
from typing import List, Dict, Tuple

class Chore:
    name: str
    amount: int

class User:
    name: str

class Chore_Scheduler:
    def __init__(self, chores: List[Chore], users: List[User]):
        self.chores = chores
        self.users = users
        self.chore_list = self.generate_chore_list()
        self.schedule = self.create_initial_schedule()

    def generate_chore_list(self):
        chore_list = {}
        for chore in self.chores:
            chore_list.extend([chore.name] * chore.amount)
        return chore_list
    
    def create_initial_schedule(self):
        schedule = {}

        for user in self.users:
            schedule[user] = {}
            

                
        return schedule

if __name__ == "__main__":
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


    
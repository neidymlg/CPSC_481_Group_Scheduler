import random
import math
from flask import Flask, request, jsonify
from typing import List, Dict, Tuple

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
        self.users = sorted(users, key=lambda x: x.max_chores, reverse=True)
        self.total_chores = sum(chore.amount for chore in self.chores)
        self.schedule = self.create_initial_schedule()


    def create_initial_schedule(self) -> Dict[str, List[str]]:
            schedule = {user.name: [] for user in self.users}
            n = len(self.users)
            start_index = 0  

            #splits about half of the chores to each user
            for chore in self.chores:
                for i in range(chore.amount):
                    user = self.users[(start_index + i) % n]
                    schedule[user.name].append(chore.name)
                start_index = (start_index + chore.amount) % n

            return schedule

    def evaluation_function(self, schedule):
        score = 100
        user_copy = {user.name: user for user in self.users}

        for chore_name, person_name in schedule.items():
            user_copy[person_name] += 1

        # get the amount of chores a user can do and check if there is 
        # more than usual over everywhere (unless everyone is overloaded),
        # if less than usual it's okay, if no one is overloaded except one penalize
        # decrease score if overloaded, increase score if not overloaded
        return score
        

    def get_neighbors(self, schedule: Dict[str, List[str]], num_swaps):
        schedule = self.schedule
        neighbors = []
        user_names = list(schedule.keys())

        for i in range(num_swaps):
            schedule_copy = {k: v.copy() for k, v in schedule.items()}
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
        temp = initial_temp

        for i in range(max_iterations):
            neighbors = self.get_neighbors(current_schedule, (self.total_chores * 2))
            evaluation_scores = []
            # for schedule in schedule_list:
            #     evaluation_scores.append(evaluation_function(self, schedule))
            
            # for scores in evaluation_scores:
            #     if scores < 100:
            #         evaluation_scores = (probability using delta/temperature)

            # choose a random score in the evaluation score 
        raise NotImplementedError



#if __name__ == "__main__":

#    chore_list = list([Chore("dishes", 3), Chore("cooking", 4), Chore("trash", 1), Chore("mopping", 2)])
#   user_list = list([User("User_1", max_chores=2), User("User_2", max_chores=8)])
#    cs = Chore_Scheduler(chore_list, user_list)
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


app = Flask(__name__)

@app.post("/schedule")
def make_schedule():
    data = request.get_json()

    chores = [
       Chore(c["name"], int(c["amount"]))
        for c in data.get("chores", [])
       if c.get("name") and int(c.get("amount", 0)) > 0
    ]

    users = [
       User(u["name"], int(u["max_chores"]))
       for u in data.get("users", [])
       if u.get("name")
    ]

    scheduler = Chore_Scheduler(chores, users)
    return jsonify({"schedule": scheduler.schedule})


if __name__ == "__main__":
    app.run(debug=True)
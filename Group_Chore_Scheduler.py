import random
import math
from flask import Flask, request, jsonify
from typing import List, Dict
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
        if difficulty is None or len(difficulty) == 0 or all(d == 0 for d in difficulty):
            self.difficulty = None
        else:
            self.difficulty = difficulty
        if hated_chores is None or len(hated_chores) == 0:
            self.hated_chores = []
        else:
            self.hated_chores = hated_chores
        if loved_chores is None or len(loved_chores) == 0:
            self.loved_chores = []
        else:
            self.loved_chores = loved_chores

def safe_divide(numerator, denominator):
    if denominator == 0:
        return 0.0
    return numerator/denominator

class Chore_Scheduler:
    def __init__(self, chores: List[Chore], users: List[User]):
        if not users or len(users) == 0:
            raise ValueError("Cannot create schedule with no users")
        
        if not chores or len(chores) == 0:
            raise ValueError("Cannot create schedule with no chores")
        
        self.chores = chores
        self.chore_index = {chore.name: i for i, chore in enumerate(chores)}
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

    #Network fairness index
    #useful as it will rate based on even capacity (equal load)
    #distributed underload fairly
    def jains_fairness_index(self, values: np.ndarray) -> float:
        n = len(values)
        numerator = np.sum(values) ** 2
        denominator = n * np.sum(values ** 2)
        if denominator == 0:
            return 1.0
        return numerator/denominator

    #evaluates schedule scores
    def evaluation_function(self, schedule) -> float:
        #weights
        W_LOVE = 5.0
        W_HATE = -5.0
        W_DIFFICULTY = 3.0

        user_info = {user.name: user for user in self.users}
        user_names = list(schedule.keys())

        chore_counts = np.array([len(schedule[name]) for name in user_names])
        user_max_chores = np.array([user_info[name].max_chores for name in user_names])

        # ---------- Distribution of Fairness -------------
        #big penalty

        ratios = np.divide(
            chore_counts,
            user_max_chores,
            out=np.zeros_like(chore_counts, dtype=float),
            where=user_max_chores != 0
        )

        fairness_score = self.jains_fairness_index(ratios)
        score = fairness_score * 100.0

        # ---------- Overload Penalty ------------- 
        #big penalty if unequal overload, jains will distribute underload evenly
        if np.sum(ratios > 1.0) > 0 and fairness_score < 1.0:
            score -= (np.sum(np.maximum(0, ratios - 1.0))) * (1 + (1-fairness_score) * 1000)

        for user_name in user_names:
            user = user_info[user_name]
            assigned_chores = schedule[user_name]
            assigned_indices = [self.chore_index[chore] for chore in assigned_chores]

            # ---------- Preferences Bonus / Penalty -------------
            #small penalty
            loved_amount = sum(1 for id in assigned_indices if id in user.loved_chores)
            hated_amount = sum(1 for id in assigned_indices if id in user.hated_chores)
            
            diff_score = 0
            if user.difficulty:
                diff_sum = sum(user.difficulty[id] for id in assigned_indices)
                
                #scales so that if difficulty is too negative, will penalize heavily
                #if difficulty is positive, simply adds as bonus
                if diff_sum < 0:
                    scaled_diff = diff_sum / W_DIFFICULTY
                    diff_score = -1 * (scaled_diff ** 2)
                else:
                    diff_score = diff_sum * 1.0

            score += ((loved_amount * W_LOVE) + (hated_amount * W_HATE) + diff_score)

        return score

    #changes schedule pairs by swapping or giving chores   
    def get_neighbors(self, schedule: Dict[str, List[str]], num_swaps) -> List:
        neighbors = []
        user_names = list(schedule.keys())

        if len(user_names) < 2:
            return [schedule]
        
        for _ in range(num_swaps):
            schedule_copy = copy.deepcopy(schedule)
            strategy = random.choice(['reassign', 'swap'])
            user_1, user_2 = random.sample(user_names, 2)

            if len(schedule_copy[user_1]) > 0 and len(schedule_copy[user_2]) > 0 and strategy == 'swap':
                id_1 = random.randint(0, len(schedule_copy[user_1]) - 1)
                id_2 = random.randint(0, len(schedule_copy[user_2]) - 1)
                schedule_copy[user_1][id_1], schedule_copy[user_2][id_2] = schedule_copy[user_2][id_2], schedule_copy[user_1][id_1]
            elif len(schedule_copy[user_1]) > 0:
                chore_i = random.randint(0, len(schedule_copy[user_1]) - 1)
                chore = schedule_copy[user_1].pop(chore_i)
                schedule_copy[user_2].append(chore)

            neighbors.append(schedule_copy)
        return neighbors

    #evaluates which schedule is the very best based on score
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
            #good choice
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

            #records best schedule, score for final schedule, score
            if current_score > best_score:
                best_schedule = current_schedule
                best_score = current_score
            
            #reduces temperature
            temp *= cooling_rate

        return best_schedule, best_score
    
    #calculates the mean of the user's chores if they are based on best difficulty
    def calculate_ideal_difficulty(self, schedule) -> Dict[str, float]:
        user_info = {user.name: user for user in self.users}
        user_names = list(schedule.keys())
        
        ideal_averages = {}
        
        for user_name in user_names:
            user = user_info[user_name]
            assigned_chores = schedule[user_name]
            num_assigned = len(assigned_chores)
            
            # if there is nothing in difficulty, write neutral
            if not user.difficulty or num_assigned == 0:
                ideal_averages[user_name] = 0
                continue
            
            # Get all available chore difficulties for this user
            all_chore_difficulties = []
            for chore in self.chores:
                chore_idx = self.chore_index[chore.name]
                for _ in range(chore.amount):
                    all_chore_difficulties.append(user.difficulty[chore_idx])
            
            # Sort by easiest for the user
            all_chore_difficulties.sort(reverse=True)
            
            # user gets the best chores they are assigned
            ideal_chores = all_chore_difficulties[:num_assigned]
            ideal_averages[user_name] = np.mean(ideal_chores)
        
        return ideal_averages
    
    def accuracy_score(self, schedule) -> Dict:
        total_score = 0
        user_info = {user.name: user for user in self.users}
        user_names = list(schedule.keys())
        chore_counts = np.array([len(schedule[name]) for name in user_names])
        user_max_chores = np.array([user_info[name].max_chores for name in user_names])
        
        ratios = np.divide(
            chore_counts,
            user_max_chores,
            out=np.zeros_like(chore_counts, dtype=float),
            where=user_max_chores != 0
        )

        total_capacity = np.sum(user_max_chores)
        capacity_ratio = safe_divide(self.total_chores, total_capacity)

        # ---------- Fairness Score (0-70 points) -------------
        total_score += self.jains_fairness_index(ratios) * 70.0

        #for difficulty and preference
        ideal_difficulties = self.calculate_ideal_difficulty(schedule)
        difficulty_deviations = []

        total_loved_assigned = 0
        total_hated_assigned = 0
        total_loved_available = 0
        total_hated_available = 0

        for chore in self.chores:
            chore_idx = self.chore_index[chore.name]
            
            # Check if any user loves this chore
            is_loved_by_anyone = any(user.loved_chores and chore_idx in user.loved_chores for user in self.users)
            if is_loved_by_anyone:
                total_loved_available += chore.amount
            
            # Check if any user hates this chore
            is_hated_by_anyone = any(user.hated_chores and chore_idx in user.hated_chores for user in self.users)
            if is_hated_by_anyone:
                total_hated_available += chore.amount

        for user_name in user_names:
            user = user_info[user_name]
            assigned_chores = schedule[user_name]
            assigned_indices = [self.chore_index[chore] for chore in assigned_chores]

            #for preferences
            loved_amount = sum(1 for id in assigned_indices if id in user.loved_chores)
            hated_amount = sum(1 for id in assigned_indices if id in user.hated_chores)
            
            total_loved_assigned += loved_amount
            total_hated_assigned += hated_amount

            #for difficulty
            if user.difficulty:
                #gets the mean of each user's difficulty
                #calculates the difference
                #this is done so that we can calculate deviations based on difficulties tailored to user's difficulties
                #instead of calculating deviations between other user's difficulties
                diff_avg = np.mean([user.difficulty[i] for i in assigned_indices])
                ideal_avg = ideal_difficulties[user_name]
                difficulty_deviations.append(abs(diff_avg - ideal_avg))

        # ---------- Preference Score (0-10 points) ------------- 
        # Loved Chores, does not take into account overload
        if total_loved_available > 0:
            loved_ratio = safe_divide(total_loved_assigned, total_loved_available)
            total_score += max(0, loved_ratio * 5)
        else:
            total_score += 5

        # Hated chores, does not take into account overload 
        if total_hated_available > 0:
            hated_ratio = safe_divide(total_hated_assigned,total_hated_available)
            hated_score = max(0, 5 * (1.0 - hated_ratio))
            total_score += hated_score
        else:
            total_score += 5
        
        # ---------- Difficulty Score (0-20 points) -------------
        if difficulty_deviations:
            #gets mean of differences between ideal difficulty - actual difficulty
            #smaller deviations means it almost got close to getting the ideal one
            dev_avg = np.mean(difficulty_deviations)

            #gets list of all difficulties numbers to find the range 
            user_difficulties = []
            for user in self.users:
                if user.difficulty:
                    user_difficulties.extend(user.difficulty)
            
            #uses ranges so weight adjusts to difficulty scales
            if user_difficulties:
                diff_range = max(user_difficulties) - min(user_difficulties)
                weight = max(1.0, diff_range * 0.3)
            else:
                weight = 3.0
            
            #smaller scores are better, so if more smaller scores were present
            #we get a better score
            total_score += max(0, 20 * (1 - safe_divide(dev_avg, weight)))
        else:
            total_score += 20

        #results
        total_score = max(0, min(100,total_score))
        
        situation = "Normal"
        if capacity_ratio > 1.5:
            situation = "Severe Overload"
        elif capacity_ratio > 1.0:
            situation = "Overload"
        elif capacity_ratio < 0.6:
            situation = "Underload"

        score_results = "Bad"
        if total_score  >= 90:
            score_results = "Excellent"
        elif total_score  >= 80:
            score_results = "Good"
        elif total_score  >= 70:
            score_results = "Acceptable"
        elif total_score  >= 60:
            score_results = "Fair"
        elif total_score  >= 50:
            score_results = "Poor"

        user_ratios = {}
        for user_name in user_names:
            assigned = chore_counts[user_names.index(user_name)]
            capacity = user_info[user_name].max_chores
            user_ratios[user_name] = {
                'assigned': int(assigned),
                'capacity': capacity,
                'ratio': round(safe_divide(assigned, capacity), 2),
                'percentage': round(safe_divide(assigned, capacity) * 100, 1)
            }
        
        return {
            'score': round(total_score, 1),
            'situation': situation,
            'score_results': score_results,
            'user_loads': user_ratios,
            'capacity_ratio': round(capacity_ratio, 2)
        }



if __name__ == "__main__":

    chore_list = list([Chore("dishes", 1), Chore("cooking", 10), Chore("trash", 1), Chore("mopping", 1), Chore("paint", 1), Chore("sweep", 1)])
    user_list = list([User("Alice", max_chores=3, difficulty=[10,10,10,0,0,0],hated_chores=[], loved_chores=[]), 
                      User("Ben", max_chores=3, difficulty=[0,0,0,3,5,4],hated_chores=[], loved_chores=[])])
    cs = Chore_Scheduler(chore_list, user_list)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print(f"{schedule=}")
    print()
    print(f"\tQuality Score: {quality['score']}/100 {quality['score_results']}")
    print(f"\tSituation: {quality['situation']}")
    print(f"\tCapacity Ratio: {quality['capacity_ratio']}x")
    print()
    print("Individual Workloads:")
    for user_name, load in quality['user_loads'].items():
        print(f"\t{user_name}: {load['assigned']}/{load['capacity']} chores "
              f"\t({load['percentage']}% capacity, ratio={load['ratio']})")

# app = Flask(__name__)

# @app.post("/schedule")
# def make_schedule():
#     data = request.get_json()

#     chores = [
#        Chore(c["name"], int(c["amount"]))
#         for c in data.get("chores", [])
#        if c.get("name") and int(c.get("amount", 0)) > 0
#     ]

#     users = [
#        User(u["name"], int(u["max_chores"]))
#        for u in data.get("users", [])
#        if u.get("name")
#     ]

#     scheduler = Chore_Scheduler(chores, users)
#     return jsonify({"schedule": scheduler.schedule})


# if __name__ == "__main__":
#     app.run(debug=True)
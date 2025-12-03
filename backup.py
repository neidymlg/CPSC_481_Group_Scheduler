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
        
def safe_divide(numerator, denominator):
    if denominator == 0:
        return 0.0
    return numerator/denominator

class Chore_Scheduler:
    def __init__(self, chores: List[Chore], users: List[User]):
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

    def jains_fairness_index(self, values: np.ndarray) -> float:
        n = len(values)
        numerator = np.sum(values) ** 2
        denominator = n * np.sum(values ** 2)
        if denominator == 0:
            return 1.0
        return numerator/denominator

    def evaluation_function(self, schedule):
        #weights
        W_LOVE = 5.0
        W_HATE = -5.0
        W_DIFFICULTY = 3.0

        user_info = {user.name: user for user in self.users}
        user_names = list(schedule.keys())

        chore_counts = np.array([len(schedule[name]) for name in user_names])
        user_max_chores = np.array([user_info[name].max_chores for name in user_names])

        # ---------- Distribution of Fairness -------------
        ratios = chore_counts / user_max_chores
        fairness_score = self.jains_fairness_index(ratios)
        score = fairness_score * 100.0

        # ---------- Overload Penalty ------------- 
        if np.sum(ratios > 1.0) > 0 and fairness_score < 1.0:
            overload_penalty = (np.sum(np.maximum(0, ratios - 1.0))) * (1 + (1-fairness_score) * 1000)
            score -= overload_penalty

        for user_name in user_names:
            user = user_info[user_name]
            assigned_chores = schedule[user_name]
            assigned_indices = [self.chore_index[chore] for chore in assigned_chores]

            # ---------- Preferences Bonus / Penalty -------------
            loved_amount = sum(1 for id in assigned_indices if id in user.loved_chores)
            hated_amount = sum(1 for id in assigned_indices if id in user.hated_chores)
            
            # ---------- Difficulty Penalty -------------
            diff_score = 0
            if user.difficulty:
                diff_sum = sum(user.difficulty[id] for id in assigned_indices)
                
                if diff_sum < 0:
                    scaled_diff = diff_sum / W_DIFFICULTY
                    diff_score = -1 * (scaled_diff ** 2)
                else:
                    diff_score = diff_sum * 1.0

            score += ((loved_amount * W_LOVE) + (hated_amount * W_HATE) + diff_score)

        return score
            
    def get_quality_score(self, schedule) -> Dict:
        total_score = 0
        user_info = {user.name: user for user in self.users}
        user_names = list(schedule.keys())
        chore_counts = np.array([len(schedule[name]) for name in user_names])
        user_max_chores = np.array([user_info[name].max_chores for name in user_names])
        ratios = chore_counts / user_max_chores
        total_capacity = np.sum(user_max_chores)

        chore_frequency = {}
        for chore in self.chores:
            chore_idx = self.chore_index[chore.name]
            chore_frequency[chore_idx] = chore.amount
        capacity_ratio = self.total_chores / total_capacity

        # ---------- Fairness Score (0-50 points) -------------
        total_score += self.jains_fairness_index(ratios) * 50.0

        # ---------- Load Score (0-20 points) ------------- 
        means_ratio = np.mean(ratios)
        if capacity_ratio > 1.0:
            overload_dev = abs((np.max(ratios) - means_ratio) / means_ratio) 
            total_score += max(0, min(20, ((1 - overload_dev) * 10) * 2))
        else:
            underload_dev = abs((means_ratio - np.min(ratios)) / means_ratio)
            total_score += max(0, min(20, ((1 - underload_dev) * 10) * 2))

        diff_sums = []
        total_loved = 0
        total_hated = 0
        hated_penalty = 0
        # ---------- Preferences Score (0-10 points) -------------
        for user_name in user_names:
            user = user_info[user_name]
            assigned_chores = schedule[user_name]
            assigned_indices = [self.chore_index[chore] for chore in assigned_chores]

            total_loved += sum(1 for id in assigned_indices if id in user.loved_chores)
            total_hated += sum(1 for id in assigned_indices if id in user.hated_chores)

            for id in assigned_indices:
                if id in user.hated_chores:
                    chore_prevalance = chore_frequency[id] / self.total_chores
                    if chore_prevalance > 0.2:
                        hated_penalty += 0.3
                    elif chore_prevalance > 0.1:
                        hated_penalty += 0.6
                    else:
                        hated_penalty += 1.0
                        
            # ---------- Difficulty Score (0-20 points) -------------
            if user.difficulty:
                user_diff_sum  = sum(user.difficulty[id] for id in assigned_indices)
                diff_sums.append(user_diff_sum)
            else:
                diff_sums.append(0)
        diff_mean = np.mean(diff_sums)
        if diff_mean != 0:
            max_diff_dev = max(abs(d - diff_mean) / abs(diff_mean) for d in diff_sums)
            total_score += max(0, ((1 - min(1.0, max_diff_dev)) * 10) * 2)
        else:
            total_score += 20 

        loved_ratio = total_loved / self.total_chores
        total_score += min(5, loved_ratio * 5.0)
        total_score += (5 - min(5.0, hated_penalty * 0.5))

        total_score = max(0, min(100, total_score))

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
                'ratio': round(assigned / capacity, 2),
                'percentage': round((assigned / capacity) * 100, 1)
            }

        return {
            'score': round(total_score, 1),
            'situation': situation,
            'score_results': score_results,
            'user_loads': user_ratios,
            'capacity_ratio': capacity_ratio
        }



    
    def get_neighbors(self, schedule: Dict[str, List[str]], num_swaps):
        neighbors = []
        user_names = list(schedule.keys())

        for _ in range(num_swaps):
            schedule_copy = copy.deepcopy(schedule)
            strategy = random.choice(['reassign', 'swap'])
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

    chore_list = list([Chore("dishes", 5), Chore("cooking", 10), Chore("trash", 1), Chore("mopping", 1)])
    user_list = list([User("User_1", max_chores=5, difficulty=[10, 0, 0, 0], hated_chores=[1], loved_chores=[0]), 
                      User("User_2", max_chores=4, difficulty=[0, 0,0, 0], hated_chores=[0], loved_chores=[1])])
    cs = Chore_Scheduler(chore_list, user_list)
    schedule, score = cs.simulated_annealing()
    quality = cs.get_quality_score(schedule)
    print(f"{schedule=}")
    print(f"Optimization Score: {score:.2f}")
    print()
    print(f"\tQuality Score: {quality['score']}/100 - {quality['score_results']}")
    print(f"\tSituation: {quality['situation']}")
    print(f"\tCapacity Ratio: {quality['capacity_ratio']}x")
    print()
    print("Individual Workloads:")
    for user_name, load in quality['user_loads'].items():
        print(f"\t{user_name}: {load['assigned']}/{load['capacity']} chores "
              f"\t({load['percentage']}% capacity, ratio={load['ratio']})")
from Group_Chore_Scheduler import Chore, User, Chore_Scheduler

def print_test_results(test_name, cs, schedule, score, quality):
    print(f"TEST: {test_name}")
    print(f"Schedule: {schedule}")
    print()
    print(f"  Quality Score: {quality['score']}/100 ({quality['score_results']})")
    print(f"  Situation: {quality['situation']}")
    print(f"  Capacity Ratio: {quality['capacity_ratio']:.2f}x")
    print()
    print("Individual Workloads:")
    for user_name, load in quality['user_loads'].items():
        print(f"  {user_name}: {load['assigned']}/{load['capacity']} chores "
              f"({load['percentage']}% capacity, ratio={load['ratio']})")
        
# =============================================================================
# BASIC TESTS 
# =============================================================================

def test_perfect_balance():
    chores = [Chore("dishes", 2), Chore("cooking", 2), Chore("trash", 2)]
    users = [
        User("User_1", max_chores=3, difficulty=[0,0,0], hated_chores=[], loved_chores=[]),
        User("User_2", max_chores=3, difficulty=[0,0,0], hated_chores=[], loved_chores=[])
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("1. Perfect Balance", cs, schedule, score, quality)
    print("EXPECTED: 90-100")
    print()

def test_overload():
    chores = [Chore("dishes", 3), Chore("cooking", 3), Chore("trash", 3), 
              Chore("laundry", 3), Chore("vacuum", 3)]
    users = [
        User("User_1", max_chores=3),
        User("User_2", max_chores=3)
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("2. Overload", cs, schedule, score, quality)
    print("EXPECTED: 'Overload' Lower Score than 100 but still high due to fairness")
    print()

def test_underload():
    chores = [Chore("dishes", 1), Chore("cooking", 1)]
    users = [
        User("User_1", max_chores=5),
        User("User_2", max_chores=5),
        User("User_3", max_chores=5)
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("3. Underload", cs, schedule, score, quality)
    print("EXPECTED: Lower score due to improper fairness")
    print()

def test_strong_preferences():
    chores = [Chore("dishes", 2), Chore("cooking", 2), Chore("trash", 2)]
    users = [
        User("User_1", max_chores=3, 
             hated_chores=[0],  # Hates dishes
             loved_chores=[1]), # Loves cooking
        User("User_2", max_chores=3,
             hated_chores=[1],  # Hates cooking
             loved_chores=[0])  # Loves dishes
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("4a. Strong Preferences", cs, schedule, score, quality)
    print("EXPECTED: User_1 gets cooking, User_2 gets dishes")
    print()

def test_weak_preferences():
    chores = [Chore("dishes", 2), Chore("cooking", 2), Chore("trash", 2)]
    users = [
        User("User_1", max_chores=3, 
             hated_chores=[0],  # Hates dishes
             loved_chores=[]),
        User("User_2", max_chores=3,
             hated_chores=[], 
             loved_chores=[2])  # Loves trash
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("4b. Weak Preferences", cs, schedule, score, quality)
    print("EXPECTED: User_1 shouldn't get dishes, User_2 gets trash")
    print()

def test_difficulty():
    chores = [Chore("dishes", 1), Chore("cooking", 1), Chore("trash", 1), 
              Chore("laundry", 1), Chore("vacuum", 1), Chore("mop", 1)]
    users = [
        User("User_1", max_chores=3,
             difficulty=[5, 5, 5, -5, -5, -5]),
        User("User_2", max_chores=3,
             difficulty=[-5, -5, -5, 5, 5, 5])
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("5. Difficulty", cs, schedule, score, quality)
    print("EXPECTED: User_1 should get dishes, cooking, and trash, User_2 gets laundry, vacuum, and mop")
    print()

def test_unequal_capacity():
    chores = [Chore("dishes", 2), Chore("cooking", 2), Chore("trash", 2), Chore("laundry", 2)]
    users = [
        User("User_1", max_chores=2),
        User("User_2", max_chores=6)
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("6. Unequal Capacity", cs, schedule, score, quality)
    print("EXPECTED: 80-100 if fair even if overloaded")
    print()

def test_single_user():
    chores = [Chore("dishes", 2), Chore("cooking", 1)]
    users = [User("User_1", max_chores=5)]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("7. Single User", cs, schedule, score, quality)
    print("EXPECTED: 90-100, will be fair with one user")
    print()

def test_everyone_hates_everything():
    chores = [Chore("dishes", 1), Chore("cooking", 1), Chore("trash", 1), Chore("laundry", 1)]
    users = [
        User("User_1", max_chores=2, hated_chores=[0,1,2,3]),
        User("User_2", max_chores=2, hated_chores=[0,1,2,3])
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("8. Everyone Hates Everything", cs, schedule, score, quality)
    print("EXPECTED: Should get a -5 penalty. 80-95")
    print()

def test_complex_scenario():
    chores = [Chore("dishes", 2), Chore("cooking", 2), Chore("trash", 1), 
              Chore("laundry", 2), Chore("vacuum", 1)]
    users = [
        User("User_1", max_chores=3,
             difficulty=[3, -2, 5, -1, 2],
             hated_chores=[1],
             loved_chores=[0, 2]),
        User("User_2", max_chores=4,
             difficulty=[-1, 4, -2, 3, -1],
             hated_chores=[2],
             loved_chores=[1, 3]),
        User("User_3", max_chores=2,
             difficulty=[1, 1, 1, 1, 1],
             loved_chores=[1])
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("9. Complex Scenario", cs, schedule, score, quality)
    print("EXPECTED: Difficulty matters more than preferences. User_1 will not get cooking and will probably get dishes and laundry.")
    print("User_2 will probably get cooking and laundry. User_3 will hopefully get cooking.")
    print()

def test_zero_chores():
    chores = []
    users = [User("User_1", max_chores=3), User("User_2", max_chores=3)]
    try:
        cs = Chore_Scheduler(chores, users)
        schedule, score = cs.simulated_annealing()
        quality = cs.accuracy_score(schedule)
        print_test_results("10. Zero Chores", cs, schedule, score, quality)
        print("UNEXPECTED: Should have raised ValueError")
    except ValueError as e:
        print("TEST 10: Zero Chores")
        print(f"ERROR CAUGHT (Expected): {e}")
    print()

def test_no_users():
    chores = [Chore("dishes", 2), Chore("cooking", 1)]
    users = []
    try:
        cs = Chore_Scheduler(chores, users)
        schedule, score = cs.simulated_annealing()
        quality = cs.accuracy_score(schedule)
        print_test_results("11. No Users", cs, schedule, score, quality)
        print("UNEXPECTED: Should have raised ValueError")
    except ValueError as e:
        print("TEST 11: No Users")
        print(f"ERROR CAUGHT (Expected): {e}")
    print()

def test_single_chore_many_users():
    chores = [Chore("dishes", 1)]
    users = [
        User("User_1", max_chores=3),
        User("User_2", max_chores=3),
        User("User_3", max_chores=3),
        User("User_4", max_chores=3)
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("12. Single Chore, Many Users", cs, schedule, score, quality)
    print("EXPECTED: Will get a low score due to fairness. 50-80")
    print()

def test_all_preferences_empty():
    chores = [Chore("dishes", 2), Chore("cooking", 2)]
    users = [
        User("User_1", max_chores=2, difficulty=[0, 0], hated_chores=[], loved_chores=[]),
        User("User_2", max_chores=2, difficulty=[], hated_chores=None, loved_chores=None)
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("13. All Preferences Empty", cs, schedule, score, quality)
    print("EXPECTED: Will split evenly and randomly. 90-100")
    print()

def test_extreme_difficulty():
    chores = [Chore("chore_1", 2), Chore("chore_2", 2)]
    users = [
        User("User_1", max_chores=2, difficulty=[10, -10]),
        User("User_2", max_chores=2, difficulty=[-10, 10])
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("14a. Extreme Difficulty", cs, schedule, score, quality)
    print("EXPECTED: User_1 will want chore_1 and User 2 will want chore_2.")

    print()

def test_extreme_one_sided_difficulty():
    chores = [Chore("chore_1", 3), Chore("chore_2", 3)]
    users = [
        User("User_1", max_chores=3, difficulty=[0, 0]),
        User("User_2", max_chores=3, difficulty=[-10, -10])
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("14b. One Sided Difficulty", cs, schedule, score, quality)
    print("EXPECTED: Due to accessibility, User_2 will hopefully get less chores (1-2)")
    print()

def test_one_sided_difficulty_limited_capacity():
    chores = [Chore("chore_1", 5), Chore("chore_2", 3)]
    users = [
        User("User_1", max_chores=4, difficulty=[0, 0]),
        User("User_2", max_chores=2, difficulty=[-10, -10])
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("14c. One Sided Difficulty with limited capacity", cs, schedule, score, quality)
    print("EXPECTED: Due to fairness, User_2 will hopefully not get any chores taken.")
    print()

def test_overload_difficulty():
    chores = [Chore("chore_1", 20), Chore("chore_2", 3)]
    users = [
        User("User_1", max_chores=4, difficulty=[0, 0]),
        User("User_2", max_chores=4, difficulty=[-10, -10])
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("14d. Overload with extreme diffivulty", cs, schedule, score, quality)
    print("EXPECTED: Due to accessibility, User_2 will get less maximum chores than User_1.")
    print()

def test_love_vs_hate():
    chores = [Chore("chore_1", 1), Chore("chore_2", 1), Chore("chore_3", 1), Chore("chore_4", 1)]
    users = [
        User("User_1", max_chores=2, loved_chores=[0, 1, 2, 3]),
        User("User_2", max_chores=2, hated_chores=[0, 1, 2, 3])
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("15a. Love vs Hate", cs, schedule, score, quality)
    print("EXPECTED: Since one user loves all chores and other hates all chores, should be random.")
    print()

def test_conflicting_love():
    chores = [Chore("chore_1", 1), Chore("chore_2", 2), Chore("chore_3", 2), Chore("chore_4", 1)]
    users = [
        User("User_1", max_chores=3, loved_chores=[0, 1, 2]),
        User("User_2", max_chores=3, hated_chores=[0], loved_chores=[1,2])
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("15b. Conflicting Love", cs, schedule, score, quality)
    print("EXPECTED: User_2 will not get chore_1. Hopefully both users will get one of each of chore_2 and chore_3")
    print()

def test_conflicting_hate():
    chores = [Chore("chore_1", 1), Chore("chore_2", 2), Chore("chore_3", 2), Chore("chore_4", 1)]
    users = [
        User("User_1", max_chores=3, hated_chores=[0, 1]),
        User("User_2", max_chores=3, hated_chores=[1,2], loved_chores=[0])
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("15c. Conflicting Hate", cs, schedule, score, quality)
    print("EXPECTED: User_2 will get chore_1 as it is loved. Since User_2 hates chore_3 it should go to Chore_1." \
    "Hopefully both users will get one of each of chore_2 since they are hated.")
    print()

def test_massive_overload():
    chores = [Chore(f"chore{i}", 2) for i in range(10)]
    users = [User("User_1", max_chores=1), User("User_2", max_chores=1)]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("16. Massive Overload (10x)", cs, schedule, score, quality)
    print("EXPECTED: Even with overload, should still be fair so 90-100.")
    print()

def test_zero_capacity_user():
    chores = [Chore("dishes", 2), Chore("cooking", 2)]
    users = [User("User_1", max_chores=4), User("User_2", max_chores=0)]
    try:
        cs = Chore_Scheduler(chores, users)
        schedule, score = cs.simulated_annealing()
        quality = cs.accuracy_score(schedule)
        print_test_results("17. Zero Capacity User", cs, schedule, score, quality)
        print("EXPECTED: Adds a 1 to any users with 0")
    except Exception as e:
        print(f"Caught Error: {e}")
    print()

def test_all_zero_capacity():
    chores = [Chore("dishes", 1)]
    users = [User("User_1", max_chores=0), User("Bob", max_chores=0)]
    try:
        cs = Chore_Scheduler(chores, users)
        schedule, score = cs.simulated_annealing()
        quality = cs.accuracy_score(schedule)
        print_test_results("18. All Zero Capacity", cs, schedule, score, quality)
        print("EXPECTED: Adds a 1 to any users with 0")
    except Exception as e:
        print(f"Caught Error: {e}")
    print()

def test_many_same_chores():
    chores = [Chore("dishes", 50)]
    users = [
        User("User_1", max_chores=20),
        User("User_2", max_chores=20),
        User("User_3", max_chores=10)
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("19. Many Same Chores", cs, schedule, score, quality)
    print(f"EXPECTED: All fairness 90-100")
    print()

def test_three_way_imbalance():
    chores = [Chore("chore_1", 2), Chore("chore_2", 2), Chore("chore_3", 2)]
    users = [
        User("Weak", max_chores=1),
        User("Average", max_chores=3),
        User("Strong", max_chores=9)
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("21. Three-way Capacity Imbalance", cs, schedule, score, quality)
    print(f"EXPECTED: Lower score due to underload 70-100")
    print()

# =============================================================================
# ENHANCED TESTS (22-50+)
# =============================================================================
def test_extreme_overload_100x():
    chores = [Chore(f"chore_{i}", 1) for i in range(100)]
    users = [User("user_0", max_chores=1)]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing(max_iterations=1000)
    quality = cs.accuracy_score(schedule)
    print_test_results("21. Extreme Overload 100x", cs, schedule, score, quality)
    print("90-100 as there is only one user to redistribute")

def test_extreme_underload_100x():
    chores = [Chore("chore_0", 1)]
    users = [User(f"user_{i}", max_chores=1) for i in range(100)]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing(max_iterations=1000)
    quality = cs.accuracy_score(schedule)
    print_test_results("22. Extreme Underload 100x", cs, schedule, score, quality)
    print("30-50 as it is not fair to some users that they get more chores than others.")

def test_love_overrides_difficulty():
    chores = [Chore("chore_0", 2), Chore("chore_1", 2)]
    users = [
        User("user_0", max_chores=2, difficulty=[-10, 10], loved_chores=[0]),
        User("user_1", max_chores=2, difficulty=[10, -10], loved_chores=[1]),
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing(max_iterations=1500)
    quality = cs.accuracy_score(schedule)
    print_test_results("28. Love Overrides Difficulty", cs, schedule, score, quality)
    print("Should not get loved chores due to difficulty, so user_0 should get chore_1 and user_1 chore_0")

def test_imbalanced_love():
    chores = [Chore("chore_0", 2), Chore("chore_1", 4), Chore("chore_2", 2)]
    users = [
        User("user_0", max_chores=3, loved_chores=[0]),
        User("user_1", max_chores=3, loved_chores=[0]),
        User("user_2", max_chores=3, loved_chores=[0]),
        User("user_3", max_chores=3, hated_chores=[1]),
        User("user_4", max_chores=3),
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing(max_iterations=2000)
    quality = cs.accuracy_score(schedule)
    print_test_results("32. Imbalanced Love Distribution", cs, schedule, score, quality)
    print("user 0 - 3 should randomly get one of chore_0")

def test_partial_overlap():
    chores = [Chore("chore_0", 2), Chore("chore_1", 2), Chore("chore_2", 2), Chore("chore_3", 2)]
    users = [
        User("user_0", max_chores=3, difficulty=[10, 5, -5, 0], loved_chores=[0, 1]),
        User("user_1", max_chores=3, difficulty=[5, 10, 0, -5], loved_chores=[1, 2]),
        User("user_2", max_chores=3, difficulty=[0, -5, 10, 5], loved_chores=[2, 3]),
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing()
    quality = cs.accuracy_score(schedule)
    print_test_results("33. Partial Overlap Preferences", cs, schedule, score, quality)
    print("Preference tiebreakers will be broken by difficulty.")

def test_all_negative_difficulties():
    chores = [Chore("chore_0", 2), Chore("chore_1", 2), Chore("chore_2", 2)]
    users = [
        User("user_0", max_chores=3, difficulty=[-5, -10, -1]),
        User("user_1", max_chores=3, difficulty=[-8, -3, -7]),
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing(max_iterations=1500)
    quality = cs.accuracy_score(schedule)
    print_test_results("36. All Difficulties Negative", cs, schedule, score, quality)
    print("Chooses least negative assignment, as such chore_1 should always go to user_1")

def test_all_positive_difficulties():
    chores = [Chore("chore_0", 2), Chore("chore_1", 2), Chore("chore_2", 2)]
    users = [
        User("user_0", max_chores=3, difficulty=[5, 10, 1]),
        User("user_1", max_chores=3, difficulty=[8, 3, 7]),
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing(max_iterations=1500)
    quality = cs.accuracy_score(schedule)
    print_test_results("37. All Difficulties Positive", cs, schedule, score, quality)
    print("Chooses positive, as such chore_1 will go to user_0")

def test_mixed_preference_types():
    chores = [Chore("chore_0", 2), Chore("chore_1", 2), Chore("chore_2", 2), Chore("chore_3", 2)]
    users = [
        User("user_0", max_chores=3, difficulty=[5, -5, -3, -1], loved_chores=[2]),
        User("user_1", max_chores=3, difficulty=[-5, 0, 5, -2], loved_chores=[1]),
        User("user_2", max_chores=3, difficulty=[6, -4, 0, 8], hated_chores=[3]),
        User("user_3", max_chores=3, difficulty=[1, 1, 1, 1]),
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing(cooling_rate=0.002)
    quality = cs.accuracy_score(schedule)
    print_test_results("41. Mixed Preference Types", cs, schedule, score, quality)
    print("Even though user_0 has a negative difficulty for a loved chore, as long as it isn't too great in comparison with other users, it should assign it.")
    print("Additionally, user_2 hates a chore they can easily do, so it shouldn't be fully assigned to do all of them.")

def test_weak_mixed_preference_types():
    chores = [Chore("chore_0", 2), Chore("chore_1", 2), Chore("chore_2", 2), Chore("chore_3", 2)]
    users = [
        User("user_0", max_chores=3, difficulty=[5, -5, -1, -1], loved_chores=[2]),
        User("user_1", max_chores=3, difficulty=[-5, 0, 5, -2], loved_chores=[1]),
        User("user_2", max_chores=3, difficulty=[2, -4, 0, 5], hated_chores=[3]),
        User("user_3", max_chores=3, difficulty=[1, 1, 1, 1]),
    ]
    cs = Chore_Scheduler(chores, users)
    schedule, score = cs.simulated_annealing(cooling_rate=0.06)
    quality = cs.accuracy_score(schedule)
    print_test_results("41. Weaker Mixed Preference Types", cs, schedule, score, quality)
    print("Now that we have gotten less conflicting difficulties, user_2 should get none of chore_3 and user_0 should get all chore_2")


# =============================================================================
# RUN ALL TESTS
# =============================================================================
if __name__ == "__main__":
    
    #Basic Tests
    # test_perfect_balance() 
    # test_overload() 
    # test_underload()
    # test_strong_preferences() 
    # test_weak_preferences()
    # test_difficulty() 
    # test_unequal_capacity()
    # test_single_user() 
    # test_everyone_hates_everything() 
    # test_complex_scenario()
    # test_zero_chores() 
    # test_no_users() 
    # test_single_chore_many_users()
    # test_all_preferences_empty() 
    # test_extreme_difficulty() 
    # test_extreme_one_sided_difficulty()
    # test_one_sided_difficulty_limited_capacity()
    # test_overload_difficulty()
    # test_love_vs_hate()
    # test_conflicting_love()
    # test_conflicting_hate()
    # test_massive_overload() 
    # test_zero_capacity_user() 
    # test_all_zero_capacity()
    # test_many_same_chores() 
    # test_three_way_imbalance()
    
    # Enhanced tests 
    # test_extreme_overload_100x() 
    # test_extreme_underload_100x()
    # test_love_overrides_difficulty()
    # test_imbalanced_love()
    # test_partial_overlap()
    # test_all_negative_difficulties() 
    # test_all_positive_difficulties()
    # test_mixed_preference_types() 
    # test_weak_mixed_preference_types()

   
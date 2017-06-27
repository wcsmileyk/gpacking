import random
import itertools
import knapsack


def gen_gear():

    rand_nums = []
    gear = ['tent', 'fly', 'poles', 'stakes', 'filter', 'firstaid', 'lighters', 'coffee', 'water', 'hammock']
    for i in range(10):
        rand_nums.append(random.randint(1, 999))
    return tuple(zip(gear, rand_nums))


def get_bags(gear, bag_cnt, percents):

    total = 0
    for item in gear:
        total += item[1]

    bags = {}

    for i in range(bag_cnt):
        bags[i] = {'weight': 0, 'target': total * percents[i], 'gear': []}

    return bags


def use_knapsack(gear, bags):
    result = []
    size = []
    weight = []
    gear_index = []
    i = 0
    for item in gear:
        gear_index.append((item[0], i))
        i += 1
        size.append(item[1])
        weight.append(item[1])
    for bag in bags:
        capacity = round(bags[bag]['target'])
        best_match = knapsack.knapsack(size, weight).solve(capacity)
        result.append(best_match)
    return gear_index, result









def get_best(gear, target):

    max_weight = round(target + (target * .10))

    possibilities = []
    gear_perms = itertools.permutations(gear)

    for perm in gear_perms:
        bag = []
        current_weight = 0
        for item in perm:
            if item[1] + current_weight <= max_weight:
                bag.append(item)
                current_weight += item[1]
        difference = abs(target - current_weight)
        possibilities.append((difference, bag))

    best_combo = ()

    for possibility in possibilities:
        if len(best_combo) < 2:
            best_combo = possibility
        else:
            if possibility[0] < best_combo[0]:
                best_combo = possibility

    return best_combo




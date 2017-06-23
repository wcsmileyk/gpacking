import random

def gen_gear():
    rand_nums = []
    gear = ['tent', 'fly', 'poles', 'stakes', 'filter', 'firstaid', 'lighters', 'coffee', 'water', 'hammock']
    for i in range(10):
        rand_nums.append(random.randint(1, 999))
    return dict(zip(gear, rand_nums))


def breakdown(gear, weight):
    bag = {}
    current_weight = 0
    left_gear = {}
    for item in gear:
        if gear[item] + current_weight <= weight:
            bag[item] = gear[item]
            current_weight += gear[item]
        else:
            left_gear[item] = gear[item]

    return {"bag": bag, "leftover": left_gear}


def divide_bags(gear, ratio):
    total = 0
    for i in gear:
        total += gear[i]

    weights = [total * r for r in ratio]

    bags = {}

    for weight in weights:
        breakdown(gear, weight)

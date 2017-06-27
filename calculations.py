import random
import itertools
"""
So the goal here is to take all shared gear, and break it down as close to the desired percentage as possible amongst
participants (2 or more). For example:

I have 10 items of shared gear of varying weights, all greater than 0. 

I have 2 backpackers, and I want the more experience packer to carry 70% of the shared equipment. And the less experienced
to carry 30% to makeup for their differing conditioning levels.

I've looked at bin packing and knapsack problems and attempted a permutation calculation you'll see below. But this
appears different because all gear must go, and I can go over the max weight. It's not capacity, but target distribution
based.

The direction my brain wants to lead in goes something like this:

Fill all the bags to capacity:

for item in gear:
    for bag in bags:
        if item + sum(bag) <= bag_target:
            bag.append(item)
            gear.remove(item)

Now try to overfill the least possible:

for item in gear:
    abs_values = []
    for bag in bags:
        abs_difference = abs(bag_target - (item + bag))
        abs_values.append((bag, abs_difference))
    
    goes_in = min(abs_values)
    goes_in[0].append(item)
    

Now the part I can't think of, would be to then take each item in each bag and compare to see if it could be more
in another bag.



"""


# I've used this to generate some dummy gear lists to work with.
def gen_gear():

    rand_nums = []
    gear = ['tent', 'fly', 'poles', 'stakes', 'filter', 'firstaid', 'lighters', 'coffee', 'water', 'hammock']
    for i in range(10):
        rand_nums.append(random.randint(1, 999))
    return tuple(zip(gear, rand_nums))


# Used to break things down, since bag count should be arbitrary. Probably lots of better ways to do this
def get_bags(gear, bag_cnt, percents):

    total = 0
    for item in gear:
        total += item[1]

    bags = {}

    for i in range(bag_cnt):
        bags[i] = {'weight': 0, 'target': total * percents[i], 'gear': []}

    return bags


# Here I'm attempting a knapsack problem. This seems to work really well for filling one bag at a time. Though I suspect
# it's going to result in additional bags not being able to be as efficient as possible.
def knapsack(m_weight, weights, target, n):
    if n == 0 or m_weight == 0:
        return 0
    if weights[n-1] > m_weight:
        return knapsack(m_weight, weights, target, n-1)
    else:
        return min(
            abs(target - (weights[n-1] + knapsack(m_weight - weights[n-1], weights, target, n-1))),
            abs(target - knapsack(m_weight, weights, target, n-1))
        )


# This was a permutation attempt. It will probably have the same problems as the knapsack problem, and it too slow to
# be realistic
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




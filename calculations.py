import random
import itertools


# I've used this to generate some dummy gear lists to work with.
def gen_gear(count):

    rand_nums = []
    gear = [
        'tent', 'fly', 'poles', 'stakes', 'filter', 'firstaid', 'lighters', 'coffee', 'water', 'hammock', 'another',
        'keep going', 'whoohoo', 'thingy', 'majig', 'bag', 'food', 'camera', 'stuff',
        'Writing', 'programs', 'or', 'programming', 'is', 'a', 'very', 'creative', 'and', 'rewarding', 'activity',
        'You', 'can', 'write', 'programs', 'for', 'many', 'reasons', 'ranging', 'from', 'making', 'your', 'living',
        'to', 'solving', 'a', 'difficult', 'data', 'analysis', 'problem', 'to', 'having', 'fun', 'to', 'helping',
        'someone', 'else', 'solve', 'a', 'problem', 'This', 'book', 'assumes', 'that'
    ]
    for i in range(count):
        rand_nums.append(random.randint(1, 500))
    return tuple(zip(gear, rand_nums))


# Used to break things down, since bag count should be arbitrary. Probably lots of better ways to do this
def get_bags(gear, bag_cnt, percents):

    total = sum([item[1] for item in gear])

    bags = [{'items': [], 'target': round(total * percents[i]), 'weight': 0} for i in range(bag_cnt)]

    return bags


def makeup_percents(count):
    percents = [
        [
            [.65, .45],
            [.8, .2],
            [.5, .5]
        ],
        [
            [.5, .3, .2],
            [.33, .33, .33],
            [.7, .2, .1]
        ],
        [
            [.25, .25, .25, .25],
            [.6, .2, .1, .1],
            [.4, .3, .15, .15]
        ],
        [
            [.2, .2, .2, .2, .2],
            [.5, .2, .1, .1, .1],
            [.4, .2, .2, .1, .1]
        ],
        [
            [.166, .166, .166, .166, .166, .166],
            [.3, .25, .2, .2, .05, .05],
            [.2, .2, .2, .2, .1, .1]
        ],
        [
            [.142, .142, .142, .142, .142, .142, .142,],
            [.2, .2, .2, .1, .1, .1, .1],
        ],
        [
            [.125, .125, .125, .125, .125, .125, .125, .125],
            [.2, .2, .1, .1, .1, .1, .1, .1],
        ],
        [
            [.11, .11, .11, .11, .11, .11, .11, .11, .11],
            [.25, .1, .1, .1, .1, .1, .1, .1, .1]
        ],
        [
            [.1, .1, .1, .1, .1, .1, .1, .1, .1, .1],
            [.25, .25, .0625, .0625, .0625, .0625, .0625, .0625, .0625, .0625]
        ]
    ]

    return random.choice(percents[count-2])


def distribute(count, item_count):
    gear = sorted(gen_gear(item_count), key=lambda wt: wt[1], reverse=True)

    percents = sorted(makeup_percents(count))

    bags = get_bags(gear, count, percents)

    targets = [bag['target'] for bag in bags]

    for item in gear:
        for i, target in enumerate(targets):
            max_weight = target
            if item[1] + bags[i]['weight'] <= max_weight:
                bags[i]['items'].append(item)
                bags[i]['weight'] += item[1]
                break

    return bags


def main(iterations):
    count = random.randint(2, 10)
    item_count = random.randint(count * 3, 63)

    results = []

    while iterations > 0:
        bags = distribute(count, item_count)
        for bag in bags:
            target = bag['target']
            weight = bag['weight']
            results.append(round(abs(target - weight) / weight, 4))

        iterations -= 1

    # for bag in bags:
    #     print(bag)

    return results


if __name__ == '__main__':
    print(main(1000))



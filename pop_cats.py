from app import db
from app.models import Category, Type


def create_types():
    types = {
            'Packs/Bags': [
                              'Backpack',
                              'Daypack',
                              'Fanny Pack',
                              'Butt Pack',
                              'Stuff Sack',
                              'Rain Cover',
                              'Pack Liner',
                              'Dry Sack',
                              'Accessory Pouch',
                              'Water Bottle Holder'
                                 ],
            'Shelter': [
                            'Tent',
                            'Tarp',
                            'Footprint',
                            'Rigging Line',
                            'Tent Poles',
                            'Rain Fly',
                            'Stakes',
                            'Bivouac Sack',
                            'Bug Net'
                               ],
            'Sleep System': [
                                 'Sleeping Bag',
                                 'Quilt',
                                 'Sleeping Bag Liner',
                                 'Sleeping Pad',
                                 'Hammock',
                                 'Under Quilt',
                                 'Hammock Suspension',
                                 'Pillow'
                                    ],
            'Clothes': [
                            'Base Layer',
                            'Socks',
                            'Pants',
                            'Shirts',
                            'Rain Shell',
                            'Fleece',
                            'Jacket',
                            'Vest',
                            'Hats',
                            'Gloves',
                            'Footwear',
                               ],
            'Kitchen': [
                            'Bear Canister',
                            'Stove',
                            'Pot',
                            'Dishes',
                            'Utensils',
                            'Cleaning',
                            'Water Filter',
                            'Water Bag',
                            'Lighter',
                            'Windscreen',
                            'Coffee Maker'
                               ],
            'Administrative': [
                                   'Map',
                                   'Compass',
                                   'Binoculars',
                                   'Writing Utensil',
                                   'Notebook',
                                   'Radio',
                                   'Altimeter',
                                   'GPS',
                                   'Flashlight/Headlamp',
                                      ],
            'Emergency/Repair': [
                                     'First Aid Kit',
                                     'Paracord',
                                     'Patch kit',
                                     'Tape',
                                     'Needles',
                                     'Thread',
                                     'Bungees'
                                        ],
            'Toiletries': [
                               'Toothbrush',
                               'Toothpaste',
                               'Deodorant',
                               'Baby Wipes',
                               'Shampoo',
                               'Soap',
                               'Conditioner',
                               'Camp Shower',
                               'Spade',
                               'Toilet Paper',
                               'Hand sanitizer',
                               'Brush/Comb'
                                  ],
            'Photography': [
                                'Lens',
                                'Camera'
                                'Tripod/Monopod',
                                'Flash',
                                'Lens Filter',
                                'Battery',
                                'Digital Storage',
                                'Remote',
                                'Case'
                                   ],
            'Entertainment': [
                                  'e-reader',
                                  'Book',
                                  'Cards',
                                  'MP3 Player',
                                  'Tablet',
                                  'Games'
                                     ],
            'Consumables': [
                                'Food',
                                'Fuel',
                                'Water',
                                'Condiments',
                                'Coffee'
                                   ]
        }

    type_ids = {}

    packs = 'Packs/Bags'
    shelter = 'Shelter'
    sleep = 'Sleep System'
    clothes = 'Clothes'
    kitchen = 'Kitchen'
    admin = 'Administrative'
    er = 'Emergency/Repair'
    hygiene = 'Toiletries'
    photo = 'Photography'
    ent = 'Entertainment'
    cons = 'Consumables'

    cats = [packs, shelter, sleep, clothes, kitchen, admin, er, hygiene, photo, ent, cons]

    for cat in cats:
        category = Category(name=cat)
        db.session.add(category)
        db.session.commit()


    for cat in cats:
        row = Category.query.filter_by(name=cat).first()
        print(cat)
        print(row)
        print(row.id)
        type_ids[row.id] = types[cat]

    for cat in type_ids:
        for item in type_ids[cat]:
            print(item)
            item_row = Type(name=item, cat_id=cat)
            db.session.add(item_row)
            db.session.commit()

if __name__ == '__main__':
    create_types()




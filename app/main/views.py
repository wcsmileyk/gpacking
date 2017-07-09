from flask import render_template, session, redirect, url_for, flash, request, jsonify
from . import main
from ..models import User, Closet, Activity, Category, Type, Item, Group, PackingList, GroupList
from flask_login import login_required, current_user
from .forms import CreatePackingList, AddItem, CreateGroup, FriendRequest, UpdateGroupList
from app import db




# Index / Main route
@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html')


# User Pages
@main.route('/home/<username>')
@login_required
def home(username):
    user = User.query.filter_by(username=username).first()
    return render_template('user/home.html', user=user)


@main.route('/closet/<username>', methods=['GET', 'POST'])
@login_required
def closet(username):
    user = User.query.filter_by(username=username).first()
    form = AddItem()
    categories = Category.query.order_by('name')
    form.category.choices = [(c.id, c.name) for c in categories]
    form.type.choices = [(t.id, t.name) for t in Type.query.order_by('name')]
    if form.validate_on_submit():
        item = Item(
            name=form.name.data,
            cat_id=form.category.data,
            type_id=form.type.data,
            weight=form.weight.data
        )
        db.session.add(item)
        db.session.commit()
        user.closet.items.append(item)
        db.session.commit()
    return render_template('user/closet.html', user=user, form=form, categories=categories)


@main.route('/friends/<username>', methods=['GET', 'POST'])
@login_required
def friends(username):
    user = User.query.filter_by(username=username).first()
    form = FriendRequest()
    if form.validate_on_submit():
        if form.user_email.data:
            friend = User.query.filter_by(email=form.user_email.data).first()
        elif form.username.data:
            friend = User.query.filter_by(username=form.username.data).first()
        user.request_friend(friend)
        db.session.commit()
    user_friends = user.my_friends()
    return render_template('user/friends.html', user=user, friends=user_friends, form=form)


@main.route('/messages/<username>')
@login_required
def messages(username):
    user = User.query.filter_by(username=username).first()
    return render_template('user/messages.html', user=user)


# Group pages
@main.route('/groups/<username>', methods=['GET', 'POST'])
@login_required
def groups(username):
    user = User.query.filter_by(username=username).first()
    form = CreateGroup()
    user_friends = [User.query.filter_by(id=friend.requested_id).first() for friend in user.friend_requested.all()]
    item_choices = [(i.id, i.name) for i in user.closet.items.order_by('cat_id').order_by('type_id').all()]
    friend_choices = [(f.id, f.username) for f in user_friends if user.friend_status(f) == 1]
    form.activity.choices = [(a.id, a.name) for a in Activity.query.order_by('name')]
    form.items.choices = item_choices
    form.shared_items.choices = item_choices
    form.friends.choices = friend_choices
    friend_count = len(friend_choices)
    if form.validate_on_submit():
        group = Group(
            name=form.name.data,
            activity_id=form.activity.data
        )
        db.session.add(group)
        db.session.commit()
        group_list = GroupList(
            group_id=group.id,
            user_id=user.id
        )
        db.session.add(group_list)
        db.session.commit()
        user.group.append(group)
        user.group_lists.append(group_list)
        for friend in form.friends.data:
            f = User.query.get(friend)
            f.group.append(group)
            gl = GroupList(user_id=f.id, group_id=group.id)
            db.session.add(gl)
            db.session.commit()
            f.group_lists.append(gl)
        db.session.commit()
        for item in form.items.data:
            group_list.items.append(Item.query.get(item))
        for s_item in form.shared_items.data:
            group.shared_items.append(Item.query.get(s_item))
        db.session.commit()
    user_groups = user.group.all()
    return render_template('user/groups.html', user=user, groups=user_groups, form=form, row_count=friend_count, friend_choices=friend_choices, item_choices=item_choices)


@main.route('/group/<groupname>')
@login_required
def manage_group(groupname):
    user = current_user
    group = Group.query.filter_by(name=groupname).first()
    categories = Category.query.order_by('name')
    return render_template('user/manage_group.html', group=group, user=user, categories=categories)


@main.route('/group/<groupname>/<username>', methods=['GET', 'POST'])
@login_required
def manage_bag(groupname, username):
    group = Group.query.filter_by(name=groupname).first()
    user = User.query.filter_by(username=username).first()
    group_list = GroupList.query.filter_by(group_id=group.id, user_id=user.id).first()
    categories = Category.query.order_by('name')
    form = UpdateGroupList()
    item_choices = [(i.id, i.name) for i in user.closet.items.order_by('cat_id').order_by('type_id').all()]
    form.items.choices = item_choices
    form.category.choices = [(c.id, c.name) for c in categories]
    # TODO: Add validation
    if request.method == 'POST':
        if len(form.items.data) >= 1:
            for item in form.items.data:
                i = Item.query.get(item)
                group_list.items.append(i)
                db.session.commit()
        else:
            item = Item(name=form.name.data, cat_id=form.category.data, type_id=form.type.data, weight=form.weight.data)
            db.session.add(item)
            db.session.commit()
            user.closet.items.append(item)
            group_list.items.append(item)
            db.session.commit()
    weights = [i.weight for i in group_list.items.all()]
    return render_template('user/manage_bag.html', user=user, form=form, group=group, categories=categories, group_list=group_list, weights=weights, item_choices=item_choices)


@main.route('/group/<groupname>/shared')
@login_required
def manage_shared(groupname):
    form = UpdateGroupList()
    user = current_user
    group = Group.query.filter_by(name=groupname).first()
    categories = Category.query.order_by('name')
    form.items.choices = [(i.id, i.name) for i in user.closet.items.order_by('cat_id').order_by('type_id').all()]
    form.category.choices = [(c.id, c.name) for c in categories]
    return render_template('user/manage_shared.html', user=user, form=form, group=group, categories=categories)


# Packing Lists
@main.route('/packing_lists/<username>', methods=['GET', 'POST'])
@login_required
def packing_lists(username):
    user = User.query.filter_by(username=username).first()
    form = CreatePackingList()
    form.activity.choices = [(a.id, a.name) for a in Activity.query.order_by('name')]
    form.items.choices = [(i.id, i.name) for i in user.closet.items.order_by('cat_id').order_by('type_id').all()]
    item_choices = [(i.id, i.name) for i in user.closet.items.order_by('cat_id').order_by('type_id').all()]
    if form.validate_on_submit():
        pl = PackingList(
            name=form.name.data,
            activity_id=form.activity.data,
            user_id=user.id
        )
        db.session.add(pl)
        db.session.commit()
        for item in form.items.data:
            pl.items.append(Item.query.get(item))
        db.session.commit()
    pls = user.packing_lists
    return render_template('user/packing_list.html', user=user, packing_lists=pls, form=form, item_choices=item_choices)


@main.route('/update_packing_list/<packing_list>', methods=['GET', 'POST'])
@login_required
def update_packing_list(packing_list):
    user = User.query.filter_by(username=current_user.username).first()
    pl = PackingList.query.filter_by(name=packing_list).first()
    form = AddItem()
    categories = Category.query.order_by('name')
    form.category.choices = [(c.id, c.name) for c in categories]
    form.type.choices = [(t.id, t.name) for t in Type.query.order_by('name')]
    form.items.choices = [(i.id, i.name) for i in user.closet.items.order_by('cat_id').order_by('type_id').all()]
    item_choices = [(i.id, i.name) for i in user.closet.items.order_by('cat_id').order_by('type_id').all()]
    if request.method == 'POST':
        print(len(form.items.data))
        if len(form.items.data) >= 1:
            for item in form.items.data:
                i = Item.query.get(item)
                pl.items.append(i)
                db.session.commit()
        else:
            item = Item(
                name=form.name.data,
                cat_id=form.category.data,
                type_id=form.category.data,
                weight=form.weight.data
            )
            db.session.add(item)
            db.session.commit()
            pl.items.append(item)
            user.closet.items.append(item)
            db.session.commit()
    weights = [i.weight for i in pl.items.all()]
    return render_template('user/update_packing_list.html', user=user, form=form, pl=pl, categories=categories, weights=weights, item_choices=item_choices)



@main.route('/create_opts')
def create_opts():
    cat = request.args.get('a', type=int)
    types = [name for name in Type.query.filter_by(cat_id=cat).with_entities(Type.id, Type.name)]
    return jsonify(result=types)


@main.route('/delete_inv/<inv_id>')
def delete_inv(inv_id):
    inventory = Closet.query.get(int(inv_id))
    db.session.delete(inventory)
    db.session.commit()
    return redirect(url_for('main.profile', username=current_user.username))

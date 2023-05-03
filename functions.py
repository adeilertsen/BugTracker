from db import *
from forms import *
from datetime import date
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user


def get_table_data(tablename):
    return db.session.query(tablename).all()


def update_form_choices(choices, tablename):
    for item in db.session.query(tablename).all():
        if item.name not in choices:
            choices.append(item.name)


def get_bugform_data(form):
    data = Bug(
            title=form.title.data,
            description=form.description.data,
            reporter=current_user.name,
            status=0,
            date=date.today(),
            assigned=User.query.filter_by(name=form.assign.data).first(),
            priority=form.priority.data,
            project_id=form.project.data
        )
    return data


def add_item_to_db(item):
    db.session.add(item)
    db.session.commit()


def user_exist():
    email = request.form['email']
    if User.query.filter_by(email=email).first():
        return True
    else:
        return False


def get_form_data_register():
    new_user = User(
        name=request.form['name'],
        email=request.form['email'],
        password=generate_password_hash(request.form['password'], "pbkdf2:sha256", 8)
    )
    return new_user


def add_user_to_db():
    new_user = get_form_data_register()
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)


def form_is_submitted():
    if request.method == "POST":
        return True
    else:
        return False


def is_password_correct():
    user = User.query.filter_by(email=request.form["email"]).first()
    password = request.form["password"]
    if check_password_hash(user.password, password):
        return True


def get_user():
    user = User.query.filter_by(email=request.form["email"]).first()
    return user


def fill_edit_form(bug):
    form = NewBugForm(
        title=bug.title,
        description=bug.description,
        project=bug.project_id,
        assign=bug.assigned,
        priority=bug.priority,
    )
    return form


def update_bug(bug, new_data):
    bug.title = new_data.title.data
    bug.description = new_data.description.data
    bug.project_id = new_data.project.data
    bug.assigned = User.query.filter_by(name=new_data.assign.data).first()
    bug.priority = new_data.priority.data
    db.session.commit()


def get_commentform_data(form, bug):
    data = Comment(
        text=form.body.data,
        comment_author=current_user,
        parent_bug=bug
    )
    return data


def delete_comment(comment_id):
    comment_to_delete = Comment.query.get(comment_id)
    db.session.delete(comment_to_delete)
    db.session.commit()

def delete_bug(bug_id):
    bug_to_delete = Bug.query.get(bug_id)
    db.session.delete(bug_to_delete)
    db.session.commit()


def change_bug_status(bug_id):
    bug = Bug.query.get(bug_id)
    bug.status = bug.status + 1
    db.session.commit()

def get_projectform_data(form):
        data = Project(
            name=form.title.data,
            creator=current_user.name
        )
        return data
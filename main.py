from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, logout_user
from flask_bootstrap import Bootstrap
from flask_gravatar import Gravatar
import os
from functions import *


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "8BYkEfBA6O6donzWlSihBXox7C0sKR6b")

Bootstrap(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", 'sqlite:///bugtracker.db' )
db.init_app(app)

lm = LoginManager()
lm.init_app(app)

gravatar = Gravatar(app, size=64, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False,
                    base_url=None)


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def home():
    bugs_data = get_table_data(Bug)
    project_data = get_table_data(Project)

    update_form_choices(ASSIGN, User)
    update_form_choices(PROJECT, Project)

    form = NewBugForm()
    if form.validate_on_submit():
        new_bug = get_bugform_data(form)
        add_item_to_db(new_bug)
        return redirect(url_for("home"))

    return render_template("index.html", form=form, logged_in=current_user.is_authenticated, bugs=bugs_data,
                           project=project_data)


@app.route("/register", methods=["GET", "POST"])
def register():
    if form_is_submitted():
        if user_exist():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for("login"))
        add_user_to_db()
        return redirect(url_for("home"))
    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route("/login", methods=["GET", "POST"])
def login():
    if form_is_submitted():
        if not user_exist():
            flash("No user with that email")
            return redirect(url_for("login"))
        elif not is_password_correct():
            flash("Incorrect Password")
            return redirect(url_for("login"))
        else:
            login_user(get_user())
            return redirect(url_for("home"))
    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route("/bug/<int:index>", methods=["GET", "POST"])
def bug(index):
    project_data = get_table_data(Project)
    bugs_data = get_table_data(Bug)

    current_bug = Bug.query.get(index)
    bug_comments = current_bug.comment

    comment_form = CommentForm()
    edit_form = fill_edit_form(current_bug)
    if edit_form.validate_on_submit():
        update_bug(current_bug, edit_form)
        return redirect(url_for("bug", index=index))

    if comment_form.validate_on_submit():
        new_comment = get_commentform_data(comment_form, current_bug)
        add_item_to_db(new_comment)
        return redirect(url_for("bug", index=index))

    return render_template("bug.html", bug=current_bug, form=edit_form, comment_form=comment_form, comments=bug_comments,
                           logged_in=current_user.is_authenticated, bugs=bugs_data, project=project_data)


@app.route("/delete/<int:bug_id>")
def delete(bug_id):
    delete_bug(bug_id)
    return redirect(url_for("home"))


@app.route("/delete-comment/<int:comment_id>")
def delete_bug_comment(comment_id):
    delete_comment(comment_id)
    return redirect(url_for("home"))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/status/<int:bug_id>", methods=["GET", "POST"])
def status_change(bug_id):
    change_bug_status(bug_id)
    return redirect(url_for("bug", index=bug_id))


@app.route("/project/<int:index>", methods=["GET", "POST"])
def project(index):
    bugs_data = get_table_data(Bug)
    project_data = get_table_data(Project)
    project = Project.query.get(index)
    return render_template("project.html", bugs=bugs_data, project=project_data, current_project=project, logged_in=current_user.is_authenticated)


@app.route("/newproject", methods=["GET", "POST"])
def create_project():
    form = NewProjectForm()
    if form.validate_on_submit():
        new_project = get_projectform_data(form)
        add_item_to_db(new_project)
        return redirect(url_for("home"))

    return render_template("new-project.html", form=form)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

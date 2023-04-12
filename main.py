from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_bootstrap import Bootstrap
from sqlalchemy.orm import relationship
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from flask_gravatar import Gravatar
from datetime import date
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "8BYkEfBA6O6donzWlSihBXox7C0sKR6b")

Bootstrap(app)

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", 'sqlite:///bugtracker.db' )
db.init_app(app)

lm = LoginManager()
lm.init_app(app)

gravatar = Gravatar(app, size=64, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False,
                    base_url=None)


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Bug(db.Model):
    __tablename__ = "bug"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    reporter = db.Column(db.String, db.ForeignKey("user.name"))
    date = db.Column(db.String(250), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.String(250), nullable=False)
    project_id = db.Column(db.String, db.ForeignKey("project.name"))

    comment = relationship("Comment", back_populates="parent_bug")
    assigned = relationship("User", back_populates="bugs")


project_user = db.Table("project_user",
                        db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
                        db.Column("project_id", db.Integer, db.ForeignKey("project.id"))
                        )


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False, unique=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    bugs = relationship("Bug", back_populates="assigned")
    comments = relationship("Comment", back_populates="comment_author")
    projects = db.relationship("Project", secondary=project_user, back_populates="users")


class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.String, db.ForeignKey("user.name"))
    bug_id = db.Column(db.Integer, db.ForeignKey("bug.id"))
    comment_author = relationship("User", back_populates="comments")
    parent_bug = relationship("Bug", back_populates="comment")


class Project(db.Model):
    __tablename__ = "project"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False, unique=True)
    users = db.relationship("User", secondary=project_user, back_populates="projects")


with app.app_context():
    db.create_all()

PRIORITY = ["Low", "Medium", "High"]
ASSIGN = []
PROJECT = []
with app.app_context():
    for user in db.session.query(User).all():
        ASSIGN.append(user.name)
    for project in db.session.query(Project).all():
        PROJECT.append(project.name)


class NewBugForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    project = SelectField("Choose Project", choices=PROJECT)
    assign = SelectField("Assign Dev", choices=ASSIGN)
    priority = SelectField("Priority", choices=PRIORITY)
    submit = SubmitField("Register")


class CommentForm(FlaskForm):
    body = TextAreaField("Leave your comment here:", validators=[DataRequired()])
    submit = SubmitField("Comment")


@app.route("/", methods=["GET", "POST"])
def home():
    bugs_data = db.session.query(Bug).all()
    for user in db.session.query(User).all():
        if user.name not in ASSIGN:
            ASSIGN.append(user.name)
    for project in db.session.query(Project).all():
        if project.name not in PROJECT:
            PROJECT.append(project.name)
    form = NewBugForm()
    if form.validate_on_submit():
        new_bug = Bug(
            title=form.title.data,
            description=form.description.data,
            reporter=current_user.name,
            status=0,
            date=date.today(),
            assigned=User.query.filter_by(name=form.assign.data).first(),
            priority=form.priority.data,
            project_id=form.project.data
        )
        db.session.add(new_bug)
        db.session.commit()
        print("entry successfull")
        return redirect(url_for("home"))
    print("nothing yet")
    return render_template("index.html", form=form, logged_in=current_user.is_authenticated, bugs=bugs_data)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form['email']
        password = generate_password_hash(request.form['password'], "pbkdf2:sha256", 8)
        if User.query.filter_by(email=email).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for("login"))
        new_user = User(
            name=request.form['name'],
            email=email,
            password=password
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["username"]).first()
        password = request.form["password"]
        if not user:
            flash("No user with that email")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash("Incorrect Password")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route("/bug/<int:index>", methods=["GET", "POST"])
def bug(index):
    bug = Bug.query.get(index)
    comment_form = CommentForm()
    comments = db.session.query(Comment).filter_by(bug_id=index)
    edit_form = NewBugForm(
        title=bug.title,
        description=bug.description,
        project=bug.project_id,
        assign=bug.assigned,
        priority=bug.priority,
    )
    if edit_form.validate_on_submit():
        bug.title = edit_form.title.data
        bug.description = edit_form.description.data
        bug.project_id = edit_form.project.data
        bug.assigned = User.query.filter_by(name=edit_form.assign.data).first()
        bug.priority = edit_form.priority.data
        db.session.commit()
        return redirect(url_for("bug", index=index))
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("post"))

        new_comment = Comment(
            text=comment_form.body.data,
            comment_author=current_user,
            parent_bug=bug
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("bug", index=index))
    return render_template("bug.html", bug=bug, form=edit_form, comment_form=comment_form, comments=comments,
                           logged_in=current_user.is_authenticated)


@app.route("/delete/<int:bug_id>")
def delete(bug_id):
    bug_to_delete = Bug.query.get(bug_id)
    db.session.delete(bug_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/delete-comment/<int:comment_id>")
def delete_comment(comment_id):
    comment_to_delete = Comment.query.get(comment_id)
    db.session.delete(comment_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/status/<int:bug_id>", methods=["GET", "POST"])
def status_change(bug_id):
    bug = Bug.query.get(bug_id)
    bug.status = bug.status + 1
    db.session.commit()
    return redirect(url_for("bug", index=bug_id))

@app.route("/projects", methods=["GET", "POST"])
def create_projects():
    project1 = Project(name="BugTracker")
    project2 = Project(name="MyPortfolio")
    project3 = Project(name="Test")
    db.session.add(project1)
    db.session.add(project2)
    db.session.add(project3)
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

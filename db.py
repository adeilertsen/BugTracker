from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship


db = SQLAlchemy()


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
    project = relationship("Project", back_populates="bugs")
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
    creator = db.Column(db.String, db.ForeignKey("user.name"))
    bugs = relationship("Bug", back_populates="project")

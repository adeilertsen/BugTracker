from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired

PRIORITY = ["Low", "Medium", "High"]
ASSIGN = []
PROJECT = []


class NewBugForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    project = SelectField("Choose Project", choices=PROJECT)
    assign = SelectField("Assign Dev", choices=ASSIGN)
    priority = SelectField("Priority", choices=PRIORITY)
    submit = SubmitField("Register")


class NewProjectForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    submit = SubmitField("Register")


class CommentForm(FlaskForm):
    body = TextAreaField("Leave your comment here:", validators=[DataRequired()])
    submit = SubmitField("Comment")
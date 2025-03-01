from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField


class RegisterForm(FlaskForm):
    email = EmailField("Email:", validators=[DataRequired()])
    name = StringField("Name:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Sign Up!")


class LoginForm(FlaskForm):
    email = EmailField("Email:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Sign In!")


class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")

class CreateQueueForm(FlaskForm):
    name = StringField("Queue Name", validators=[DataRequired()])
    submit = SubmitField("Create Queue")
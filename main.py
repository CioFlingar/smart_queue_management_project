from datetime import datetime
from typing import List
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///queue.db"
app.config["SECRET_KEY"] = "SOmething"

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# user table (each user can be in multiple queue positions)
class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)

    # one user can have multiple queue positions (one-to-many)
    queue_positions: Mapped[List["QueueUser"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

# queue table (each queue has multiple positions)
class Queue(db.Model):
    __tablename__ = "queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # one queue can have multiple queue positions (one-to-many)
    queue_positions: Mapped[List["QueueUser"]] = relationship(
        back_populates="queue", cascade="all, delete-orphan"
    )

# queue position table (mapping users to queues)
class QueueUser(db.Model):
    __tablename__ = "queue_position"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    queue_id: Mapped[int] = mapped_column(ForeignKey("queue.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    position: Mapped[int] = mapped_column(Integer, nullable=False)  # position in the queue
    status: Mapped[str] = mapped_column(String(20), default='waiting')  # waiting, completed, canceled
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # relationship backlinks
    queue: Mapped["Queue"] = relationship(back_populates="queue_positions")
    user: Mapped["User"] = relationship(back_populates="queue_positions")

#create tables
with app.app_context():
    db.create_all()




class RegisterForm(FlaskForm):
    email = EmailField("Email:", validators=[DataRequired()])
    name = StringField("Name:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Sign In!")

class LoginForm(FlaskForm):
    email = EmailField("Email:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Sign In!")

class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")





@app.route("/")
def home():
    return render_template("index.html")

# register endpoint
@app.route("/register", methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        result = db.session.execute()
    return render_template("register.html", form=register_form)


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/queues", methods=["GET", "POST"])
def queues():
    return render_template("queues.html")

@app.route("/queue_details", methods=["GET", "POST"])
def queue_details():
    return render_template("queue_detail.html", queue="")

if __name__ == "__main__":
    app.run(debug=True)
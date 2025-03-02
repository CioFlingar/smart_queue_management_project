import os
from datetime import datetime
from functools import wraps
from typing import List

from flask import Flask, render_template, flash, url_for, abort, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, login_user, current_user, logout_user, UserMixin, login_required
from twilio.rest import Client
from flask_mail import Mail, Message

# importing forms
from forms import RegisterForm, LoginForm, CreateQueueForm


#Initializing app
app = Flask(__name__)

# configuring ckeditor
ckeditor = CKEditor(app)
#adding bootstrap
Bootstrap5(app)
app.config["SECRET_KEY"] = "SOmething"

#twilio setup

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Flask-Mail setup
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")


mail = Mail(app)

def send_sms(to, message):
    client.messages.create(
        to=to,
        from_=TWILIO_PHONE_NUMBER,
        body=message
    )

def send_email(to, subject, message):
    msg = Message(subject, recipients=[to], body=message, sender="your_email@gmail.com")
    mail.send(msg)

#configuring login manager
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)



#initializing database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///queue.db"


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)


# user table (each user can be in multiple queue positions)
class User(UserMixin, db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
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
    positions: Mapped[List["QueueUser"]] = relationship(
        back_populates="queue", cascade="all, delete-orphan"
    )


# queue position table (mapping users to queues)
class QueueUser(db.Model):
    __tablename__ = "queue_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    queue_id: Mapped[int] = mapped_column(ForeignKey("queue.id"), nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    position: Mapped[int] = mapped_column(Integer, nullable=False)  # position in the queue
    status: Mapped[str] = mapped_column(String(20), default='waiting')  # waiting, completed, canceled
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # relationship backlinks
    queue: Mapped["Queue"] = relationship(back_populates="positions")
    user: Mapped["User"] = relationship(back_populates="queue_positions")


#create tables
with app.app_context():
    db.create_all()


#create an admin-only decorator
def admin_only(func):
    @wraps(func)
    def decorator_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.id == 1:
            return abort(403)
        return func(*args, **kwargs)
    return decorator_function



@app.route("/")
def home():
    queues = Queue.query.all()
    return render_template("index.html", queues=queues)


# register endpoint
@app.route("/register", methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        result = db.session.execute(db.select(User).where(User.email == register_form.email.data))
        user = result.scalar()
        if user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        hashed_and_salted_password = generate_password_hash(
            register_form.password.data,
            method="pbkdf2:sha256",
            salt_length=4
        )
        new_user = User(
            email=register_form.email.data,
            username=register_form.name.data,
            password_hash=hashed_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        #login the user here
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("register.html", form=register_form, current_user=current_user)

# login endpoint
@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password_hash, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html", form=login_form, current_user=current_user)


# logout endpoint
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


#Create queue sections
@app.route("/create_queue", methods=["GET","POST"])
@login_required
def create_queue():
    form = CreateQueueForm()
    if form.validate_on_submit():
        new_queue = Queue(
            name = form.name.data,
        )
        db.session.add(new_queue)
        db.session.commit()
        flash("Queue created successfully!", "success")
        return redirect(url_for("queues"))
    return render_template("create_queue.html", form=form)


#show all the queue sections
@app.route("/queues", methods=["GET"])
def queues():
    all_queues = Queue.query.all()
    print(all_queues)
    return render_template("queues.html", queues=all_queues)


# view queue details
@app.route("/queue_details/<int:queue_id>", methods=["GET"])
def queue_details(queue_id):
    queue = db.get_or_404(Queue, queue_id)
    users_in_queue = db.session.query(QueueUser).filter(QueueUser.queue_id == queue_id).order_by(QueueUser.position).all()
    return render_template("queue_detail.html", queue=queue, users=users_in_queue)


# delete specific queue section
@app.route("/delete_queue/<int:queue_id>")
@login_required
@admin_only
def delete_queue(queue_id):
    queue=db.get_or_404(Queue, queue_id)
    db.session.delete(queue)
    db.session.commit()
    return redirect(url_for('queues'))


# join in specific queue
@app.route("/join_queue/<int:queue_id>")
@login_required
def join_queue(queue_id):
    user_id = current_user.id

    last_position = db.session.query(db.func.max(QueueUser.position)).filter_by(queue_id=queue_id).scalar()
    new_position = (last_position or 0) + 1

    existing_entry = QueueUser.query.filter_by(queue_id=queue_id, customer_id=user_id).first()
    if existing_entry:
        flash("You are already in this queue!", "warning")
        return redirect(url_for("queue_details", queue_id=queue_id))

    new_entry = QueueUser(
        queue_id=queue_id,
        customer_id=user_id,
        position=new_position,
        status="waiting"
    )
    db.session.add(new_entry)
    db.session.commit()

    flash(f"You joined the queue at position {new_position}!", "success")
    return redirect(url_for("queue_details", queue_id=queue_id))


# process the queue actions and shows them
@app.route("/process_queue/<int:queue_id>/<action>", methods=["POST"])
@login_required
@admin_only
def process_queue(queue_id, action):
    user_id = int(request.form.get("user_id"))
    queue_entry = QueueUser.query.filter_by(queue_id=queue_id, customer_id=user_id).first_or_404()

    if not queue_entry:
        flash("You are not in this queue!", "danger")
        return redirect(url_for("queue_details", queue_id=queue_id))

    if action not in ["complete", "remove"]:
        flash("Invalid action!", "danger")
        return redirect(url_for("queue_details", queue_id=queue_id))

    if action == "complete":
        queue_entry.status = "completed"
    elif action == "remove":
        db.session.delete(queue_entry)

    db.session.commit()

    flash(f"Your queue status has been updated: {action}", "info")
    return redirect(url_for("queue_details", queue_id=queue_id))


# send message or mail to user
@app.route("/queue_notify/<int:queue_id>/<int:user_id>")
@login_required
def notify_user(queue_id, user_id):
    queue_entry = QueueUser.query.filter_by(queue_id=queue_id, customer_id=user_id).first_or_404()
    user = db.get_or_404(User, queue_entry.customer_id)

    send_sms(user.phone_number, f"Your turn is coming soon in queue: {queue_entry.queue_id}!")
    send_email(user.email, "Queue Update", f"Your turn is coming soon in queue: {queue_entry.queue_id}!")

    flash("User notified successfully!", "success")
    return redirect(url_for("queue_details", queue_id=queue_id))


# API endpoint to fetch queue details
@app.route("/api/queue/<int:queue_id>")
@login_required
def get_queue(queue_id):
    queue = db.get_or_404(Queue, queue_id)
    users_in_queue = db.session.query(QueueUser).filter(QueueUser.queue_id == queue_id).order_by(QueueUser.position).all()

    queue_data = {
        "id": queue.id,
        "name": queue.name,
        "users": [{"id":user.customer_id, "position":user.position, 'status': user.status} for user in users_in_queue]
    }
    return jsonify(queue_data)


if __name__ == "__main__":
    app.run(debug=True)



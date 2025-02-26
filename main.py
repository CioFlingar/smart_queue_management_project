from datetime import datetime
from typing import List
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///queue.db"

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# user table (each user can be in multiple queue positions)
class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default='customer')

    # one user can have multiple queue positions (one-to-many)
    queue_positions: Mapped[List["QueuePosition"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

# queue table (each queue has multiple positions)
class Queue(db.Model):
    __tablename__ = "queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    max_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=50)

    # one queue can have multiple queue positions (one-to-many)
    positions: Mapped[List["QueuePosition"]] = relationship(
        back_populates= "queue", cascade="all, delete-orphan"
    )

# queue position table (mapping users to queues)
class QueuePosition(db.Model):
    __tablename__ = "queue_position"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    queue_id: Mapped[int] = mapped_column(ForeignKey("queue.id"), nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    position: Mapped[int] = mapped_column(Integer, nullable=False)  # Position in the queue
    status: Mapped[str] = mapped_column(String(20), default='waiting')  # waiting, completed, canceled
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # relationship backlinks
    queue: Mapped["Queue"] = relationship(back_populates="positions")
    user: Mapped["User"] = relationship(back_populates="queue_positions")

#create tables
with app.app_context():
    db.create_all()



@app.route("/")
def home():
    return "Hello World!"



if __name__ == "__main__":
    app.run(debug=True)
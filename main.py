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

# User Table (Each user can be in multiple queue positions)
class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default='customer')

    # One user can have multiple queue positions (One-to-Many)
    queue_positions: Mapped[List["QueuePosition"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

# Queue Table (Each queue has multiple positions)
class Queue(Base):
    __tablename__ = "queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    max_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=50)

    # One queue can have multiple queue positions (One-to-Many)
    positions: Mapped[List["QueuePosition"]] = relationship(
        back_populates= "queue", cascade="all, delete-orphan"
    )

# Queue Position Table (Mapping Users to Queues)
class QueuePosition(Base):
    __tablename__ = "queue_position"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    queue_id: Mapped[int] = mapped_column(ForeignKey("queue.id"), nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    position: Mapped[int] = mapped_column(Integer, nullable=False)  # Position in the queue
    status: Mapped[str] = mapped_column(String(20), default='waiting')  # waiting, completed, canceled
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relationship Backlinks
    queue: Mapped["Queue"] = relationship(back_populates="positions")
    user: Mapped["User"] = relationship(back_populates="queue_positions")

@app.route("/")
def home():
    return "Hello World!"



if __name__ == "__main__":
    app.run(debug=True)
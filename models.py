from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    chat_id = db.Column(db.String(120), unique=True, nullable=False)
    points = db.Column(db.Integer, default=0)
    referrals = db.Column(db.JSON, default=[])
    completed_task_ids = db.Column(db.JSON, default=[])  # Track tasks completed by the user
    tasks = db.relationship("Task", backref="user", lazy=True)  # Relationship to Task


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    reward = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    url = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


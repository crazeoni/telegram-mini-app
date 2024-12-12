from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=True)
    chat_id = db.Column(db.String(120), unique=True, nullable=True)
    points = db.Column(db.Integer, default=0)
    referrals = db.Column(db.JSON, default=[])
    tasks = db.relationship("Task", backref="user", lazy=True)  # Relationship to Task


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    reward = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


class UserTask(db.Model):
    """Join table for User and Task to track completion status."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='user_tasks')
    task = db.relationship('Task', backref='user_tasks')

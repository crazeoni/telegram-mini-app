from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=True)
    chat_id = db.Column(db.BigInteger, unique=True, nullable=True)
    points = db.Column(db.Integer, default=0)
    referrals = db.relationship('Referral', backref='referrer', lazy=True)  # Referrals made by this user
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


class Referral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Referring user
    referred_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Referred user
    referred_user = db.relationship('User', foreign_keys=[referred_user_id])  # Relationship to referred user
    referral_bonus = db.Column(db.Integer, default=50)  # Bonus points for the referrer

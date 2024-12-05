from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    chat_id = db.Column(db.String(120), unique=True, nullable=False)
    points = db.Column(db.Integer, default=0)
    referrals = db.Column(db.JSON, default=[])

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    reward = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    url = db.Column(db.String(200), nullable=False)  # Add this line for the URL field

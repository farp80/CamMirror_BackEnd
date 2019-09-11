from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(25), unique=True, nullable=False)
    last_name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(25), unique=True, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, CURRENT_TIMESTAMP)

    def __repr__(self):
        return '<Users %r>' % self.username

    def serialize(self):
        return {
            "email": self.email,
            "password": self.password,
            "first_name" : self.first_name,
            "last_name": self.last_name,
            "id": self.id
        }
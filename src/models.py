from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(25), unique=False, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now(), nullable=True)

    def __repr__(self):
        return '<Users %r>' % self.email

    def serialize(self):
        return {
            "email": self.email,
            "password": self.password,
            "id": self.id
        }
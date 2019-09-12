from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(25), unique=False, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now(), nullable=True)

    class Membership(Base):
    __tablename__ = 'membership'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class Profiles(Base):
    __tablename__ = 'profiles'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    date = Column(String(250), nullable=False)
    membership_id = Column(Integer, ForeignKey('membership.id'))
    user_id = Column(Integer, ForeignKey('users.id'))


class Pictures(Base):
    __tablename__ = 'pictures'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    url = Column(String(250), nullable=False)
    date = Column(String(250), nullable=False)
    updated_date = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))



    def __repr__(self):
        return '<Users %r>' % self.email

    def serialize(self):
        return {
            "email": self.email,
            "password": self.password,
            "id": self.id
        }
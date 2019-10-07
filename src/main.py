"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import datetime
import hashlib
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from sqlalchemy import distinct
from time import sleep
from utils import APIException, generate_sitemap
from models import db, Users, Profiles, Membership, Pictures
from flask_jwt_simple import (
    JWTManager, jwt_required, create_jwt, get_jwt_identity
)
from models import Users
from sqlalchemy import distinct

app = Flask(__name__)
# Setup the Flask-JWT-Simple extension
app.config['JWT_SECRET_KEY'] = 'camMirror@4Geeks'  # Change this!
jwt = JWTManager(app)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# @app.route('/migrate_user_hash', methods=['GET'])
# def migrate_users_passwords():
#     users = Users.query.all()
#     count = 0
#     for u in users:
#         count = count + 1
#         m = hashlib.md5()
#         m.update(u.password.encode("utf-8"))
#         u.password = m.hexdigest()

#     db.session.commit()

#     return jsonify(count+" users were updated"), 200

@app.route('/user', methods=['GET'])
def get_all_users():
    users_query = Users.query.all()
    users_query = list(map(lambda x: x.serialize(), users_query))
    return jsonify(users_query), 200


@app.route('/signup', methods=['POST'])
def signup():
    if not request.get_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    params = request.get_json()
    first_name = params.get('first_name', None)
    last_name = params.get('last_name', None)
    email = params.get('email', None)
    password = params.get('password', None)

    if not first_name:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not last_name:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not email:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    if first_name == '' or last_name == '':
        return jsonify({"msg": "Need First Name and Last Name"}), 401
    if email == '' or password == '':
        return jsonify({"msg": "Bad username or password"}), 401

    people_query = Users.query.filter_by(email=email).first()
    if people_query:
        return jsonify({"msg": "User Already Exists"}), 405

    m = hashlib.md5()
    m.update(password.encode("utf-8"))
    pwdHashed = m.hexdigest()

    user1 = Users(
        first_name = first_name,
        last_name = last_name,
        email = email,
        password = pwdHashed)

    db.session.add(user1)
    db.session.commit()
    return jsonify({"msg": "User created"}), 200



@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    params = request.get_json()
    email = params.get('email', None)
    password = params.get('password', None)

    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    m = hashlib.md5()
    m.update(password.encode("utf-8"))
    pwdHashed = m.hexdigest()

    usercheck = Users.query.filter_by(email=email, password=pwdHashed).first()
    if usercheck == None:
        return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    ret = {'jwt': create_jwt(identity=email),'id': usercheck.id, 'email':usercheck.email}
    return jsonify(ret), 200


@app.route('/picture/<int:profile_id>', methods=['GET'])
def get_picture(profile_id):
    profile_picture_query = Pictures.query.filter_by(user_id = profile_id)
    all_pictures_folders = list(map(lambda x: x.serialize(), profile_picture_query))
    return jsonify(all_pictures_folders), 200


@app.route('/pictures', methods=['POST'])
def pictures():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    params = request.get_json()
    user_id = params.get('user_id', None)
    date = params.get('date', None)
    updated_date = params.get('updated_date', None)
    url = params.get('url', None)
    folder = params.get('folder', None)

    if not user_id:
        return jsonify({"msg": "Missing user_id"}), 400
    if not date:
        return jsonify({"msg": "Missing date"}), 400
    if not url:
        return jsonify({"msg": "Missing URL parameter"}), 400
    if not folder:
        return jsonify({"msg": "Missing Folder parameter"}), 400
    if not updated_date:
        return jsonify({"msg": "Missing updated_date parameter"}), 400


    picture = Pictures(
        url = url,
        date = date,
        updated_date = updated_date,
        pic_folder = folder,
        user_id = user_id)

    db.session.add(picture)
    db.session.commit()
    return jsonify({"msg": "URL Picture: " + url + " was created"}), 200

@app.route('/profile', methods=['GET'])
def get_all_profiles():
    profile_query = Profiles.query.all()
    profile_query = list(map(lambda x: x.serialize(), profile_query))
    return jsonify(profile_query), 200


@app.route('/profile', methods=['POST', 'DELETE', 'PUT'])
@jwt_required
def profile():
    if not request.get_json:
        raise APIException("You need to specify the request body as a json object", status_code=400)

    params = request.get_json()
    user_id = params.get('user_id', None)

    if request.method == 'POST':
        profile_to_check = Profiles.query.filter_by(user_id=user_id).first()
        user1 = Users.query.get(user_id)
        code = 100
        current_date = datetime.datetime.now()

        if profile_to_check is None:
            new_profile = Profiles(user_id=params['user_id'], membership_id=None)
            db.session.add(new_profile)
        else:
            profile_to_check.updated_date = current_date
            code = 150

        db.session.commit()

        response = {
            "first_name": user1.first_name,
            "last_name": user1.last_name,
            "currentUserId": user1.id,
            "created_date": user1.created_date,
            "updated_date": current_date,
            "code": code
        }

        return jsonify(response), 200

    if request.method == 'DELETE':
        profile1 = Profiles.query.get(user_id)

        if profile1 is None:
            raise APIException('Profile not found', status_code=404)

        db.session.delete(profile1)
        db.session.commit()

        return jsonify(user1.serialize()), 200

    if request.method == 'PUT':
        params = request.get_json()

        user_id = params.get('user_id', None)
        first_name = params.get('first_name', None)
        last_name = params.get('last_name', None)
        password = params.get('password', None)
        email = params.get('email', None)

        if not user_id:
            return jsonify({"msg": "Missing user_id"}), 400
        if not first_name:
            return jsonify({"msg": "Missing First Name"}), 400
        if not last_name:
            return jsonify({"msg": "Missing Last Name"}), 400
        if not email:
            return jsonify({"msg": "Missing Email"}), 400
        if not password:
            return jsonify({"msg": "Missing Password"}), 400

        current_profile = Profiles.query.get(user_id)
        user_profile_settings = Users.query.get(user_id)

        if user_profile_settings is None:
            raise APIException('User not found', status_code=404)

        if current_profile is None:
            raise APIException('Profile not found', status_code=404)

        user_profile_settings.first_name = first_name
        user_profile_settings.email = email
        user_profile_settings.last_name = last_name

        m = hashlib.md5()
        m.update(password.encode("utf-8"))
        pwdHashed = m.hexdigest()
        user_profile_settings.password = pwdHashed

        updated_date = datetime.datetime.now()
        current_profile.updated_date = updated_date

        db.session.commit()

        response = {
            "first_name": first_name,
            "last_name": last_name,
            "currentUserId": user_id,
            "updated_date": updated_date,
            "email": email
        }
        return jsonify(response), 200



@app.route('/membership', methods=['POST', 'DELETE', 'GET', 'PUT'])
@jwt_required
def membership():

    if request.method == 'GET':
        membership_query = Membership.query.all()
        membership = list(map(lambda x: x.serialize(), membership_query))
        return jsonify(membership), 200

    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400

        params = request.get_json()
        membership_name = params.get('membership_name', None)
        card_holder_name = params.get('card_holder_name', None)
        card_number = params.get('card_number', None)
        card_expiration_date = params.get('card_expiration_date', None)
        card_cvv = params.get('card_cvv', None)
        user_id = params.get('user_id', None)

        if not membership_name:
            return jsonify({"msg": "Missing membership_name parameter"}), 400

        if not card_holder_name:
            return jsonify({"msg": "Missing card_holder_name parameter"}), 400

        if not card_number:
            return jsonify({"msg": "Missing card_number parameter"}), 400

        if not card_expiration_date:
            return jsonify({"msg": "Missing card_expiration_date parameter"}), 400

        if not card_cvv:
            return jsonify({"msg": "Missing card_cvv parameter"}), 400

        new_member = Membership(
            membership_name = membership_name,
            card_holder_name = card_holder_name,
            card_number = card_number,
            card_expiration_date = card_expiration_date,
            card_cvv = card_cvv,
            user_id = params ['user_id'])

        db.session.add(new_member)
        db.session.commit()

        return jsonify(new_member), 200


    if request.method == 'PUT':
        params = request.get_json()

        user_id = params.get('user_id', None)
        membership_name = params.get('membership_name', None)
        card_holder_name = params.get('card_holder_name', None)
        card_number = params.get('card_number', None)
        card_expiration_date = params.get('card_expiration_date', None)
        card_cvv = params.get('card_cvv', None)

        if not user_id:
            return jsonify({"msg": "Missing user_id"}), 400
        if not membership_name:
            return jsonify({"msg": "Missing Membership Name"}), 400
        if not card_holder_name:
            return jsonify({"msg": "Missing Card Holder Name"}), 400
        if not card_number:
            return jsonify({"msg": "Missing Card Number"}), 400
        if not card_expiration_date:
            return jsonify({"msg": "Missing Card Expiration Date"}), 400
        if not card_cvv:
            return jsonify({"msg": "Missing Card CVV"}), 400

        print('$$hnvruhvn'+ str(user_id))

        user_member_settings = Membership.query.filter_by(user_id=user_id).first()

        if user_member_settings is None:
            raise APIException('Member not found', status_code=404)


        user_member_settings.membership_name = membership_name
        user_member_settings.card_holder_name = card_holder_name
        user_member_settings.card_number = card_number
        user_member_settings.card_expiration_date = card_expiration_date
        user_member_settings.card_cvv = card_cvv

        updated_date = datetime.datetime.now()
        user_member_settings.updated_date = updated_date

        db.session.commit()

        response = {
            "membership_name": membership_name,
            "card_holder_name": card_holder_name,
            "card_number": card_number,
            "card_expiration_date": card_expiration_date,
            "card_cvv": card_cvv,
            "currentUserId": user_id,
            "updated_date": updated_date

        }
        return jsonify(response), 200


    if request.method == 'DELETE':
        membership1 = Membership.query.get(user_id)

        if membership1 is None:
            raise APIException('Membership not found', status_code=404)

        db.session.delete(membership1)
        db.session.commit()

        return jsonify(user1.serialize()), 200

# Protect a view with jwt_required, which requires a valid jwt
# to be present in the headers.
@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    return jsonify({'jwt': get_jwt_identity()}), 200

# this only runs if `$ python src/main.py` is exercuted
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT)

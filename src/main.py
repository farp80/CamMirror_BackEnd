"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from models import db, Users, Profiles, Membership
from flask import Flask, jsonify, request
from flask_jwt_simple import (
    JWTManager, jwt_required, create_jwt, get_jwt_identity
)
from models import Users

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
    # print(first_name)
    # print(last_name)
    # print(email)
    # print(password)
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


    user1 = Users(first_name=first_name, last_name=last_name, email=email, password=password)
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

    usercheck = Users.query.filter_by(email=email, password=password).first()
    if usercheck == None:
        return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    ret = {'jwt': create_jwt(identity=email),'id': usercheck.id}
    return jsonify(ret), 200


@app.route('/profile', methods=['GET'])
def get_all_profiles():
    profile_query = Profiles.query.all()
    profile_query = list(map(lambda x: x.serialize(), profile_query))
    return jsonify(profile_query), 200

@app.route('/profile', methods=['POST', 'DELETE', 'PUT'])
@jwt_required
def profile():
    if not request.get_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    params = request.get_json()
    user_id = params.get('user_id', None)

    new_profile = Profiles(user_id=params['user_id'],membership_id=None)
    db.session.add(new_profile)
    db.session.commit()

    profilecheck = Profiles.query.filter_by(user_id=user_id).first()

    if request.method == 'DELETE':
        profile1 = Profiles.query.get(user_id)
    if profile1 is None:
        raise APIException('Profile not found', status_code=404)

    db.session.delete(profile1)
    db.session.commit()
    return jsonify(user1.serialize()), 200


    # Identity can be any data that is json serializable
    ret = {'profile_id': profilecheck.id}

    return jsonify(ret), 200

    if request.method == 'PUT':
        body = request.get_json()
    if body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)
    user1 = Contact.query.get(contact_id)
    if user1 is None:
        raise APIException('User not found', status_code=404)
    if "first_name" in body:
        user1.full_name = body["first_name"]
    if "email" in body:
        user1.email = body["email"]
    if "last_name" in body:
        user1.phone = body["last_name"]
    if "password" in body:
        user1.address = body["password"]
    db.session.commit()
    return jsonify(user1.serialize()), 200



@app.route('/profile/membership', methods=['POST', 'DELETE'])
@jwt_required
def membership():

    params = request.get_json()
    name = params.get('name', None)
    profile_id = params.get('profile_id', None)

    new_member = Membership(profile_id=params['profile_id'])
    db.session.add(new_member)
    db.session.commit()

    membershipcheck = Membership.query.filter_by(profile_id=profile_id).first()

    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    if not name:
        return jsonify({"msg": "Missing name parameter"}), 400

    if request.method == 'DELETE':
        membership1 = Membership.query.get(profile_id)
    if membership1 is None:
        raise APIException('Profile not found', status_code=404)

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

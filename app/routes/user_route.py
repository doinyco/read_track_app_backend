from flask import Blueprint, request, jsonify
from ..models.user import User, users


user_bp = Blueprint("user", __name__)


@user_bp.route("/register", methods=["POST"])
def register():

    data = request.json

    new_user = User(
        data["username"],
        data["password"]
    )

    users.append(new_user)

    return jsonify({
        "message": "User registered"
    })


@user_bp.route("/login", methods=["POST"])
def login():

    data = request.json

    for user in users:

        if user.username == data["username"] and user.password == data["password"]:

            return jsonify({
                "message": "Login successful"
            })


    return jsonify({
        "message": "Invalid username or password"
    }), 401
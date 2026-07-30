from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, request, session, jsonify
from ..models.user import User
from ..db import db


user_bp = Blueprint("user", __name__, url_prefix="/users")


@user_bp.route("/register", methods=["POST"])
def register():

    data = request.json

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({
            "message": "Username, email and password are required"
        }), 400

    new_user = User(
        email=email,
        username=username,
        password_hash=generate_password_hash(password)
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User registered"
    }), 201



@user_bp.route("/login", methods=["POST"])
def login():

    data = request.json

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "message": "Username and password are required"
        }), 400

    user = User.query.filter_by(
        username=username
    ).first()

    if user and check_password_hash(
        user.password_hash,
        password
    ):
        session["user_id"] = user.id

        return jsonify({
            "message": "Login successful"
        }), 200

    return jsonify({
        "message": "Invalid username or password"
    }), 401



@user_bp.route("/logout", methods=["GET"])
def logout():

    session.pop("user_id", None)

    return jsonify({
        "message": "Logged out"
    }), 200


@user_bp.route("/delete", methods=["DELETE"])
def delete_account():

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "message": "Not logged in"
        }), 401

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    db.session.delete(user)
    db.session.commit()

    session.pop("user_id", None)

    return jsonify({
        "message": "Account deleted"
    }), 200
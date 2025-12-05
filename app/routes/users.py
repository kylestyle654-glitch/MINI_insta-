from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import User

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("", methods=["POST"])
def create_user():
    data = request.get_json()
    user = User(
        username=data["username"],
        email=data["email"],
        password_hash=data["password_hash"],
        bio=data.get("bio"),
        avatar_url=data.get("avatar_url")
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created", "id": user.id}), 201


@users_bp.route("", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "bio": u.bio,
            "avatar_url": u.avatar_url,
            "created_at": u.created_at
        } for u in users
    ])


@users_bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.bio = data.get("bio", user.bio)
    user.avatar_url = data.get("avatar_url", user.avatar_url)
    db.session.commit()
    return jsonify({"message": "User updated"})


@users_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})

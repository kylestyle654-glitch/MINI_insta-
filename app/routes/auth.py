from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models.user import User
from app.errors import error_response

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return error_response("BAD_REQUEST", "username, email and password are required", 400)

    if User.query.filter((User.username==username)|(User.email==email)).first():
        # detect which field conflicts
        if User.query.filter_by(username=username).first():
            return error_response("RESOURCE_CONFLICT", "Username already exists", 409, {"field":"username"})
        return error_response("RESOURCE_CONFLICT", "Email already exists", 409, {"field":"email"})

    user = User(username=username, email=email, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return error_response("BAD_REQUEST", "email and password required", 400)
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return error_response("UNAUTHORIZED", "Invalid credentials", 401)
    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token, "token_type":"Bearer"}), 200

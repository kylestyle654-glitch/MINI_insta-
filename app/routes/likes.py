from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.like import Like
from app.models.post import Post
from sqlalchemy import func
from app.errors import error_response

likes_bp = Blueprint("likes", __name__, url_prefix="/posts")

@likes_bp.route("/<int:post_id>/like", methods=["POST"])
@jwt_required()
def like_post(post_id):
    user_id = int(get_jwt_identity())
    post = Post.query.get(post_id)
    if not post:
        return error_response("NOT_FOUND", "Post not found", 404)
    # idempotent: if exists, return 200 with current count
    existing = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
    if existing:
        likes_count = db.session.query(func.count(Like.user_id)).filter(Like.post_id==post_id).scalar() or 0
        return jsonify({"liked": True, "likes_count": likes_count}), 200
    like = Like(user_id=user_id, post_id=post_id)
    db.session.add(like)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error_response("INTERNAL_ERROR", "Could not add like", 500)
    likes_count = db.session.query(func.count(Like.user_id)).filter(Like.post_id==post_id).scalar() or 0
    return jsonify({"liked": True, "likes_count": likes_count}), 200

@likes_bp.route("/<int:post_id>/like", methods=["DELETE"])
@jwt_required()
def unlike_post(post_id):
    user_id = int(get_jwt_identity())
    like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
    likes_count = db.session.query(func.count(Like.user_id)).filter(Like.post_id==post_id).scalar() or 0
    return jsonify({"liked": False, "likes_count": likes_count}), 200

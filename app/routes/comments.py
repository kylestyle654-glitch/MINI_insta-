from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.errors import error_response

comments_bp = Blueprint("comments", __name__, url_prefix="/comments")

@comments_bp.route("", methods=["POST"])
@jwt_required()
def add_comment():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    post_id = data.get("post_id")
    text = (data.get("text") or "").strip()
    if not post_id or not text:
        return error_response("BAD_REQUEST", "post_id and text are required", 400)
    post = Post.query.get(post_id)
    if not post:
        return error_response("NOT_FOUND", "Post not found", 404)
    comment = Comment(post_id=post_id, author_id=user_id, text=text)
    db.session.add(comment)
    db.session.commit()
    return jsonify({"id": comment.id, "created_at": comment.created_at.isoformat() + "Z"}), 201

@comments_bp.route("/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id):
    user_id = int(get_jwt_identity())
    comment = Comment.query.get_or_404(comment_id)
    post = Post.query.get(comment.post_id)
    # only comment author or post author can delete
    if comment.author_id != user_id and post.author_id != user_id:
        return error_response("FORBIDDEN", "Not allowed to delete this comment", 403)
    db.session.delete(comment)
    db.session.commit()
    return "", 204

@comments_bp.route("/post/<int:post_id>", methods=["GET"])
def list_comments(post_id):
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        limit = 20
    try:
        offset = int(request.args.get("offset", 0))
    except ValueError:
        offset = 0
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc(), Comment.id.desc()).offset(offset).limit(limit).all()
    items = [{
        "id": c.id,
        "text": c.text,
        "created_at": c.created_at.isoformat() + "Z",
        "author": {"id": c.author.id, "username": c.author.username, "avatar_url": c.author.avatar_url}
    } for c in comments]
    return jsonify({"items": items, "paging": {"limit": limit, "offset": offset, "next_offset": offset + len(items)}}), 200

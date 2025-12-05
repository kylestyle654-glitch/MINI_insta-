from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.media import Media
from app.models.post import Post
from app.errors import error_response

media_bp = Blueprint("media", __name__, url_prefix="/media")

@media_bp.route("", methods=["POST"])
@jwt_required()
def add_media():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    post_id = data.get("post_id")
    url = data.get("url")
    if not post_id or not url:
        return error_response("BAD_REQUEST", "post_id and url are required", 400)
    post = Post.query.get(post_id)
    if not post:
        return error_response("NOT_FOUND", "Post not found", 404)
    if post.author_id != user_id:
        return error_response("FORBIDDEN", "Only author can add media", 403)
    media = Media(post_id=post_id, url=url, mime_type=data.get("mime_type"), width=data.get("width"), height=data.get("height"), order_idx=data.get("order_idx", 0))
    db.session.add(media)
    db.session.commit()
    return jsonify({"id": media.id}), 201

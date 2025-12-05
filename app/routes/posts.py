from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.post import Post
from app.models.media import Media
from app.models.user import User
from app.models.like import Like
from app.models.comment import Comment
from app.errors import error_response
from sqlalchemy import func

posts_bp = Blueprint("posts", __name__, url_prefix="/posts")

def make_rich_post(post, viewer_id=None):
    # author
    author = post.author
    # media list
    media_items = [{
        "id": m.id, "url": m.url, "mime_type": m.mime_type,
        "width": m.width, "height": m.height, "order_idx": m.order_idx
    } for m in post.media.order_by(Media.order_idx).all()]
    # stats
    likes_count = db.session.query(func.count(Like.user_id)).filter(Like.post_id==post.id).scalar() or 0
    comments_count = db.session.query(func.count(Comment.id)).filter(Comment.post_id==post.id).scalar() or 0
    liked_by_me = False
    if viewer_id:
        liked_by_me = db.session.query(Like).filter_by(post_id=post.id, user_id=viewer_id).first() is not None

    return {
        "id": post.id,
        "caption": post.caption,
        "created_at": post.created_at.isoformat() + "Z",
        "author": {"id": author.id, "username": author.username, "avatar_url": author.avatar_url},
        "media": media_items,
        "stats": {"likes_count": likes_count, "comments_count": comments_count},
        "viewer": {"liked_by_me": liked_by_me}
    }

@posts_bp.route("", methods=["POST"])
@jwt_required()
def create_post():
    data = request.get_json() or {}
    caption = data.get("caption", "").strip()
    media_list = data.get("media", [])

    if not caption:
        return error_response("BAD_REQUEST", "caption is required", 400)

    user_id = int(get_jwt_identity())
    post = Post(author_id=user_id, caption=caption)
    db.session.add(post)
    db.session.flush()  # to get post.id before commit if we add media

    # optional media items: list of dicts with url,mime_type,width,height,order_idx
    for i, m in enumerate(media_list):
        url = m.get("url")
        if not url:
            continue
        media = Media(post_id=post.id, url=url, mime_type=m.get("mime_type"), width=m.get("width"), height=m.get("height"), order_idx=m.get("order_idx", i))
        db.session.add(media)

    db.session.commit()
    return jsonify({"id": post.id, "created_at": post.created_at.isoformat() + "Z"}), 201

@posts_bp.route("", methods=["GET"])
def list_posts():
    # params: author_id (optional), limit, offset
    try:
        limit = int(request.args.get("limit", current_app.config["PAGINATION_DEFAULT_LIMIT"]))
    except ValueError:
        limit = current_app.config["PAGINATION_DEFAULT_LIMIT"]
    limit = min(limit, current_app.config["PAGINATION_MAX_LIMIT"])
    try:
        offset = int(request.args.get("offset", 0))
    except ValueError:
        offset = 0

    author_id = request.args.get("author_id", None)

    # viewer id if token present
    viewer_id = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            if identity:
                viewer_id = int(identity)
        except Exception:
            viewer_id = None

    query = Post.query
    if author_id:
        query = query.filter_by(author_id=author_id)

    # ordering: created_at desc, id desc
    posts = query.order_by(Post.created_at.desc(), Post.id.desc()).offset(offset).limit(limit).all()
    items = [make_rich_post(p, viewer_id) for p in posts]

    next_offset = offset + len(items)
    paging = {"limit": limit, "offset": offset, "next_offset": next_offset}
    return jsonify({"items": items, "paging": paging}), 200

@posts_bp.route("/<int:post_id>", methods=["GET"])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    # viewer
    viewer_id = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            if identity:
                viewer_id = int(identity)
        except Exception:
            viewer_id = None

    rp = make_rich_post(post, viewer_id)
    # include last N comments optional: ?comments_limit=5
    try:
        comments_limit = int(request.args.get("comments_limit", 0))
    except ValueError:
        comments_limit = 0
    if comments_limit > 0:
        comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc(), Comment.id.desc()).limit(comments_limit).all()
        rp["comments"] = [{
            "id": c.id, "text": c.text, "created_at": c.created_at.isoformat() + "Z",
            "author": {"id": c.author.id, "username": c.author.username, "avatar_url": c.author.avatar_url}
        } for c in comments]

    return jsonify(rp), 200

@posts_bp.route("/<int:post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id):
    user_id = int(get_jwt_identity())
    post = Post.query.get_or_404(post_id)
    if post.author_id != user_id:
        return error_response("FORBIDDEN", "You are not allowed to delete this post", 403)
    db.session.delete(post)
    db.session.commit()
    return "", 204

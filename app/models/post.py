from app.extensions import db
from datetime import datetime

class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    caption = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    author = db.relationship("User", backref=db.backref("posts", lazy="dynamic"))
    media = db.relationship("Media", backref="post", lazy="dynamic", cascade="all, delete-orphan")

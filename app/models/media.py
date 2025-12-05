from app.extensions import db

class Media(db.Model):
    __tablename__ = "media"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    url = db.Column(db.String(512), nullable=False)
    mime_type = db.Column(db.String(64))
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    order_idx = db.Column(db.Integer, default=0)

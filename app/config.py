import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, '..', 'mini_instagram.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "change_this_to_a_strong_secret"
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60  # seconds (1 hour)
    PAGINATION_DEFAULT_LIMIT = 20
    PAGINATION_MAX_LIMIT = 50

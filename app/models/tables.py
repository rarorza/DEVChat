from app import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(86), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    profile_pic = db.Column(db.String, default="default.png")
    posts = db.relationship("Post", backref="author", lazy=True)
    interests = db.Column(db.String, nullable=False, default="No info")

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)

    def verify_password(self, pwd):
        """
        Checks that the hash of the password entered by the user is compatible
        with the db
        param pwd: Password entered by the user
        """
        return check_password_hash(self.password, pwd)

    def count_posts(self):
        return len(self.posts)


class Post(db.Model):
    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    id_author = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, title, body, id_author):
        self.title = title
        self.body = body
        self.id_author = id_author

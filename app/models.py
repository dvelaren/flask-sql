import time
import jwt
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, basic_auth, token_auth
from sqlalchemy.orm import Mapped, mapped_column


@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(name=username).first()
    if user and check_password_hash(user.password, password):
        return user
    return False


@token_auth.verify_token
def verify_token(token):
    try:
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        user = User.query.filter_by(id=data["id"]).first()
    except:
        return False
    return user


class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(db.String)

    def hash_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def generate_auth_token(self, expires_in=600):
        return jwt.encode(
            {"id": self.id, "exp": time.time() + expires_in},
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    def to_dict(self):
        return {"id": self.id, "username": self.username, "email": self.email}

    @staticmethod
    def get_all():
        return db.session.execute(db.select(User).order_by(User.id)).scalars().all()

import time
import jwt
import datetime as dt
from typing import List
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, basic_auth, token_auth
from sqlalchemy.orm import Mapped, mapped_column, relationship


@basic_auth.verify_password
def verify_password(username, password):
    user = db.session.execute(
        db.select(User).filter_by(username=username)
    ).scalar_one_or_none()
    if not user or not user.verify_password(password):
        return False
    return user


@token_auth.verify_token
def verify_token(token):
    try:
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        user = db.session.execute(
            db.select(User).filter_by(id=data["id"])
        ).scalar_one_or_none()
    except:
        return False
    if not user:
        return False
    return user


class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(db.String)
    password: Mapped[str] = mapped_column(db.String)
    created_at: Mapped[dt.datetime] = mapped_column(
        db.DateTime(timezone=True),
        nullable=False,
        default=dt.datetime.now(dt.timezone.utc),
    )
    last_modified: Mapped[dt.datetime] = mapped_column(
        db.DateTime(timezone=True),
        nullable=False,
        default=dt.datetime.now(dt.timezone.utc),
    )
    posts: Mapped[List["Post"]] = relationship(back_populates="user", lazy="dynamic", cascade="all, delete")


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

    @staticmethod
    def get_all():
        return db.session.execute(db.select(User).order_by(User.id)).scalars()

    @staticmethod
    def create_admin(username, password):
        if (
            db.session.execute(
                db.select(User).filter_by(username=username)
            ).scalar_one_or_none()
            is None
        ):
            current_date = dt.datetime.now(dt.timezone.utc)
            user = User(
                username=username,
                email="admin@admin.com",
                created_at=current_date,
                last_modified=current_date,
            )
            user.hash_password(password)
            db.session.add(user)
            db.session.commit()

    def __repr__(self):
        return f"<User {self.username}>"

class Post(db.Model):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(db.String, nullable=False)
    body: Mapped[str] = mapped_column(db.String, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        db.DateTime(timezone=True),
        nullable=False,
        default=dt.datetime.now(dt.timezone.utc),
    )
    last_modified: Mapped[dt.datetime] = mapped_column(
        db.DateTime(timezone=True),
        nullable=False,
        default=dt.datetime.now(dt.timezone.utc),
    )
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="posts")

    @staticmethod
    def get_all():
        return db.session.execute(db.select(Post).order_by(Post.id)).scalars()

    def __repr__(self):
        return f"<Post {self.title}>"
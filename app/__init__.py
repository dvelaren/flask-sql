import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()
multi_auth = MultiAuth(basic_auth, token_auth)


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or b"change_me"
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql+psycopg2://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}"
        f"@localhost:5432/flask_test?client_encoding=utf8"
    )
    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app

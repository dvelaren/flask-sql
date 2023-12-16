import datetime as dt
from app import ma, db
from app.models import User
from marshmallow import (
    fields,
    validate,
    validates,
    pre_load,
    post_load,
    ValidationError,
)


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True

    id = ma.auto_field()
    username = ma.auto_field()
    email = fields.String(required=True, validate=validate.Email(error="Invalid email"))
    password = fields.String(
        required=True,
        validate=validate.Length(min=8, error="Password must contain 8 digits"),
        load_only=True,
    )
    created_at = fields.DateTime()
    last_modified = fields.DateTime()

    @pre_load
    def process_input(self, data, **kwargs):
        data["username"] = data["username"].lower().strip()
        data["email"] = data["email"].lower().strip()
        current_date = dt.datetime.now(dt.timezone.utc).isoformat()
        data["created_at"] = current_date
        data["last_modified"] = current_date
        return data

    @validates("username")
    def validates_username(self, username):
        if db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalar_one_or_none():
            raise ValidationError("That username is taken")


class UserUpdateSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True

    email = fields.String(
        required=False, validate=validate.Email(error="Invalid email")
    )
    password = fields.String(
        required=False,
        validate=validate.Length(min=8, error="Password must contain 8 digits"),
        load_only=True,
    )

    @post_load
    def update_user(self, data, **kwargs):
        data.last_modified = dt.datetime.now(dt.timezone.utc)
        return data


user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_update_schema = UserUpdateSchema()

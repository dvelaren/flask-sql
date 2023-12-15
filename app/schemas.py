from app import ma, db
from app.models import User
from marshmallow import fields, validate, validates, ValidationError, post_load


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True

    id = ma.auto_field()
    username = fields.String(required=True)
    email = fields.String(required=True, validate=validate.Email(error="Invalid email"))
    password = fields.String(
        required=True,
        validate=validate.Length(min=8, error="Password must contain 8 digits"),
        load_only=True,
    )

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

    id = ma.Integer(required=True, dump_only=True)
    email = fields.String(
        required=False, validate=validate.Email(error="Invalid email")
    )
    password = fields.String(
        required=False,
        validate=validate.Length(min=8, error="Password must contain 8 digits"),
        load_only=True,
    )


user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_update_schema = UserUpdateSchema()

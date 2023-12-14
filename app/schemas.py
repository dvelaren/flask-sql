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


class UserUpdateSchema(ma.Schema):
    __model__ = User

    id = ma.Integer(required=True, dump_only=True)
    email = fields.String(
        required=False, validate=validate.Email(error="Invalid email")
    )
    password = fields.String(
        required=False,
        validate=validate.Length(min=8, error="Password must contain 8 digits"),
        load_only=True,
    )

    @post_load
    def make_object(self, data, **kwargs):
        if "user" in self.context:
            user_model = self.context["user"]
            user_model.email = data.get("email", user_model.email)
            user_model.password = data.get("password", user_model.password)

            return self.context["user"]
        else:
            return ValidationError("User must be in context")


user_schema = UserSchema()
users_schema = UserSchema(many=True)

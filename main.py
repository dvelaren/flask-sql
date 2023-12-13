# Flask SQLAlchemy test application

from flask import request, jsonify
from app import create_app, db, multi_auth
from app.models import User

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User}


@app.cli.command("deploy")
def deploy():
    user = User(name="admin", email="admin@admin.com")
    user.hash_password("admin")
    db.session.add(user)
    db.session.commit()


@app.get("/users")
@multi_auth.login_required
def user_list():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@app.get("/users/<int:user_id>")
@multi_auth.login_required
def get_user(user_id):
    user = User.query.get(user_id)
    return jsonify(user.to_dict())


@app.get("/token")
@app.get("/login")
@multi_auth.login_required
def get_auth_token():
    expiration = 85400
    user = multi_auth.current_user()
    token = user.generate_auth_token(expiration)
    return {"token": token}


@app.post("/users")
@multi_auth.login_required
def create_user():
    data = request.get_json()
    user = User(username=data["username"], email=data["email"])
    user.hash_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return {"user": user.id}


@app.put("/users/<int:user_id>")
@multi_auth.login_required
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    for key, value in data.items():
        if key == "password":
            user.hash_password(value)
        else:
            setattr(user, key, value)
    db.session.commit()
    return {"user": user.id}


@app.delete("/users/<int:user_id>")
@multi_auth.login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return {"user": user.id}


if __name__ == "__main__":
    print("Running app...")
    app.run(debug=True, host="0.0.0.0", port=7070)

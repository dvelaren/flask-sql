# Flask SQLAlchemy test application

import os
from flask import request, jsonify, json, abort
from werkzeug.exceptions import HTTPException
from app import create_app, db, multi_auth, token_auth
from app.models import User, Post
from app.schemas import (
    user_schema,
    users_schema,
    user_update_schema,
    posts_schema,
    post_schema,
    post_update_schema,
)
from marshmallow import ValidationError

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User}


@app.cli.command("deploy")
def deploy():
    User.create_admin(
        username=os.environ.get("API_ADMIN_USERNAME") or "admin",
        password=os.environ.get("API_ADMIN_PASSWORD") or "admin",
    )


@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = json.dumps(
        {"code": e.code, "name": e.name, "description": e.description}
    )
    response.content_type = "application/json"
    return response


@multi_auth.main_auth.error_handler
@token_auth.error_handler
def auth_error(status):
    name = "Unauthorized" if status == 401 else "Forbidden"
    response = jsonify(
        {"code": status, "name": name, "description": "Invalid credentials"}
    )
    response.status_code = status
    return response


@app.get("/users")
@multi_auth.login_required
def user_list():
    users = User.get_all()
    return users_schema.dump(users)


@app.get("/users/<int:user_id>")
@multi_auth.login_required
def get_user(user_id):
    user = db.get_or_404(User, user_id, description="No users found")
    return user_schema.dump(user)


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
    try:
        user = user_schema.load(data)
    except ValidationError as err:
        abort(400, {"errors": err.messages})
    user.hash_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return {"user_id": user.id}, 201


@app.put("/users/<int:user_id>")
@multi_auth.login_required
def update_user(user_id):
    data = request.get_json()
    user = db.get_or_404(User, user_id, description="User not found")
    try:
        user = user_update_schema.load(data, instance=user, partial=True)
    except ValidationError as err:
        abort(400, {"errors": err.messages})

    if data.get("password"):
        user.hash_password(data["password"])
    db.session.commit()
    return {"user_id": user.id}


@app.delete("/users/<int:user_id>")
@multi_auth.login_required
def delete_user(user_id):
    user = db.get_or_404(User, user_id, description="User not found")
    db.session.delete(user)
    db.session.commit()
    return {"user_id": user.id}


@app.get("/posts")
@multi_auth.login_required
def post_list():
    posts = Post.get_all()
    return posts_schema.dump(posts)


@app.get("/posts/<int:post_id>")
@multi_auth.login_required
def get_post(post_id):
    post = db.get_or_404(Post, post_id, description="No posts found")
    return post_schema.dump(post)


@app.post("/posts")
@multi_auth.login_required
def create_post():
    data = request.get_json()
    try:
        post = post_schema.load(data)
    except ValidationError as err:
        abort(400, {"errors": err.messages})
    db.session.add(post)
    db.session.commit()
    return {"post_id": post.id}, 201


@app.put("/posts/<int:post_id>")
@multi_auth.login_required
def update_post(post_id):
    data = request.get_json()
    post = db.get_or_404(Post, post_id, description="Post not found")
    try:
        post = post_update_schema.load(data, instance=post, partial=True)
    except ValidationError as err:
        abort(400, {"errors": err.messages})
    db.session.commit()
    return {"post_id": post.id}


@app.delete("/posts/<int:post_id>")
@multi_auth.login_required
def delete_post(post_id):
    post = db.get_or_404(Post, post_id, description="Post not found")
    db.session.delete(post)
    db.session.commit()
    return {"post_id": post.id}

if __name__ == "__main__":
    print("Running app...")
    app.run(debug=True, host="0.0.0.0", port=7070)

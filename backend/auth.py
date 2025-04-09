from flask import Blueprint
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from backend.db import db, User

auth_bp = Blueprint('auth', __name__)

def get_is_first_user():
    return User.query.first() is None

def put_register_user(user_username, user_nom_prenoms, user_departement, user_email, user_password, user_roles):
    hashed_password = generate_password_hash(user_password)
    user = User(user_username=user_username, user_nom_prenoms=user_nom_prenoms, user_departement=user_departement, user_email=user_email, user_password=hashed_password, user_roles=user_roles)
    try:
        db.session.add(user)
        db.session.commit()
        return {"success": True}
    except IntegrityError:
        return {"success": False}

def put_update_user_infos(user_username, infos, info_type="password"):
    user = User.query.filter_by(user_username=user_username).first()
    if not user:
        print(f"User {user_username} not found.")
        return False

    column_mapping = {
        "password": "user_password",
        "email": "user_email",
        "roles": "user_roles",
        "departement": "user_departement"
    }

    if info_type == "password":
        infos = generate_password_hash(infos)

    setattr(user, column_mapping.get(info_type, info_type), infos)
    db.session.commit()
    print(f"Updated {info_type} for {user_username} to {infos}")
    return True


def get_user_infos(user_username, info_type):
    user = User.query.filter_by(user_username=user_username).first()
    if not user:
        return None
    return getattr(user, info_type)

def get_users_list():
    users = User.query.all()
    return [{"user_username": user.user_username, "user_nom_prenoms": user.user_nom_prenoms, "user_departement": user.user_departement, "user_email": user.user_email, "user_roles": user.user_roles} for user in users]
    
def put_delete_user(user_username):
    user = User.query.filter_by(user_username=user_username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return False
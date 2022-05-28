from app import db
from flask import session
import secrets
from werkzeug.security import check_password_hash, generate_password_hash

def login(username, password):
    sql = "SELECT id, password, is_admin FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return False
    else:
        if check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["is_admin"] = user.is_admin
            return True
        else:
            return False

def logout():
    del session["user_id"]
    del session["is_admin"]

def user_id():
    return session.get("user_id",0)

def is_admin():
    return session.get("is_admin", False)

def get_users():
    sql = "SELECT id, username FROM users ORDER BY username"
    result = db.session.execute(sql)
    return result.fetchall()

def register(username, password, password2, is_admin=False):
    if not username:
        return 'Username cannot be empty'
    if len(username) > 50:
        return 'Username too long (max 50 characters)'
    if not isinstance(username, str):
        return 'Username must be string'
    if not password:
        return 'Password cannot be empty'
    if not isinstance(password, str):
        return 'Password must be string'
    if not isinstance(is_admin, bool):
        return 'Admin choice must be boolean'
    if len(password) > 50:
        return 'Password too long (max 50 characters)'
    if password != password2:
        return 'Passwords differ'

    hash_value = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username,password, is_admin) VALUES (:username,:password,:is_admin)"
        db.session.execute(sql, {"username":username, "password":hash_value, "is_admin":is_admin})
        db.session.commit()
    except:
        return 'User already exists'
    if login(username, password):
        return 'OK'
    return 'Failed to login new user'

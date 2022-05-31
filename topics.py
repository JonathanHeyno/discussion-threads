from re import A
from app import db
import users

def create(name, is_hidden, have_access):
    if users.user_id() == 0 or not users.is_admin():
        return False
    try:
        sql = "INSERT INTO topics (name, is_visible, is_hidden) VALUES (:name,true,:is_hidden) RETURNING id"
        result = db.session.execute(sql, {"name":name, "is_hidden":is_hidden})
        topic_id = result.fetchone()[0]
        if is_hidden:
            for user_id in have_access:
                sql = "INSERT INTO topic_access (topic_id, user_id) VALUES (:topic_id, :user_id)"
                db.session.execute(sql, {"topic_id":topic_id, "user_id":user_id})
        db.session.commit()
        return True
    except:
        print("Tultiin exceptioniin")
        return False

def list_topics():
    if users.is_admin():
        sql = "SELECT id, name FROM topics WHERE is_visible=True ORDER BY name"
        result = db.session.execute(sql)
    else:
        sql = """SELECT DISTINCT t.id, t.name FROM topics t LEFT JOIN topic_access ta 
        ON t.id = ta.topic_id WHERE is_visible=True AND (is_hidden = False OR 
        ta.user_id = :user_id) ORDER BY t.name"""
        result = db.session.execute(sql, {"user_id":users.user_id()})
    return result.fetchall()

def get_topic_without_threads(topic_id):
    sql = "SELECT id, name, is_hidden FROM topics WHERE is_visible=TRUE AND id=:topic_id ORDER BY name"
    result = db.session.execute(sql, {"topic_id":topic_id})
    return result.fetchone()

def get_users_with_access(topic_id):
    sql = """SELECT DISTINCT u.id, u.username FROM users u LEFT JOIN topic_access ta ON u.id = ta.user_id 
    WHERE ta.topic_id=:topic_id ORDER BY u.username"""
    result = db.session.execute(sql, {"topic_id":topic_id})
    return result.fetchall()

def get_users_without_access(topic_id):
    sql = """SELECT DISTINCT u.id, u.username FROM users u LEFT JOIN (SELECT user_id FROM topic_access WHERE topic_id=:topic_id) t2 
    ON u.id = t2.user_id WHERE t2.user_id IS NULL ORDER BY u.username"""
    result = db.session.execute(sql, {"topic_id":topic_id})
    return result.fetchall()

def edit(topic_id, name, is_hidden, revoke_access, grant_access):
    sql = "UPDATE topics SET name=:name, is_hidden=:is_hidden WHERE id=:topic_id"
    db.session.execute(sql, {"topic_id":topic_id, "name":name, "is_hidden":is_hidden})
    db.session.execute("UPDATE topics SET name='KAKKAA' WHERE id=12")
    if revoke_access:
        for user_id in revoke_access:
            sql = "DELETE FROM topic_access WHERE topic_id=:topic_id AND user_id=:user_id"
            db.session.execute(sql, {"topic_id":topic_id, "user_id":user_id})
    if grant_access:
        for user_id in grant_access:
            sql = "INSERT INTO topic_access (topic_id, user_id) VALUES (:topic_id, :user_id)"
            db.session.execute(sql, {"topic_id":topic_id, "user_id":user_id})
    db.session.commit()

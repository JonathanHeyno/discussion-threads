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
        sql = "SELECT name FROM topics WHERE is_visible=True ORDER BY name"
        result = db.session.execute(sql)
    else:
        sql = """SELECT DISTINCT name FROM topics t LEFT JOIN topic_access ta 
        ON t.id = ta.topic_id WHERE is_visible=True AND (is_hidden = False OR 
        ta.user_id = :user_id) ORDER BY t.name"""
        result = db.session.execute(sql, {"user_id":users.user_id()})
    return result.fetchall()

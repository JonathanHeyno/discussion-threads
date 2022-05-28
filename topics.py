from app import db
import users

def create(name, is_hidden, have_access):
    if users.user_id() == 0 or not users.is_admin():
        return False
    try:
        sql = "INSERT INTO topics (name, is_hidden) VALUES (:name,:is_hidden)"
        db.session.execute(sql, {"name":name, "is_hidden":is_hidden})
        db.session.commit()
        print("Palautetaan topics.createssa True")
        return True
    except:
        return False

def list_topics():
    sql = "SELECT name FROM topics ORDER BY name"
    result = db.session.execute(sql)
    return result.fetchall()

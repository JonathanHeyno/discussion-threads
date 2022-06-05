from app import db
import users, topics

def create(thread_id, content):
    if users.user_id() == 0:
        return False
    try:
        sql = "INSERT INTO messages (content, thread_id, creator_id, is_visible, sent_at) VALUES (:content,:thread_id,:creator_id, True, NOW())"
        db.session.execute(sql, {"content":content, "thread_id":thread_id, "creator_id":users.user_id()})
        db.session.commit()
        return True
    except:
        return False

def list_messages(thread_id):
    sql = "SELECT id, content, creator_id, sent_at FROM messages WHERE thread_id=:thread_id AND is_visible = True ORDER BY sent_at DESC"
    result = db.session.execute(sql, {"thread_id":thread_id})
    return result.fetchall()

def new(content, thread_id):
    if users.user_id() == 0:
        return False
    try:
        sql = "INSERT INTO messages (content, thread_id, creator_id, is_visible, sent_at) VALUES (:content,:thread_id,:creator_id, True, NOW())"
        db.session.execute(sql, {"content":content, "thread_id":thread_id, "creator_id":users.user_id()})
        db.session.commit()
        return True
    except:
        return False

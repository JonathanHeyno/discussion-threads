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
    sql = """SELECT m.id, m.content, m.creator_id, m.sent_at, u.username, 
    CASE WHEN m.creator_id=:user_id THEN True ELSE False END AS is_creator FROM 
    messages m LEFT JOIN users u ON m.creator_id=u.id WHERE m.thread_id=:thread_id 
    AND m.is_visible = True ORDER BY m.sent_at DESC"""
    result = db.session.execute(sql, {"thread_id":thread_id, "user_id":users.user_id()})
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

def get_message(message_id):
    if users.user_id() == 0:
        return []
    sql = "SELECT id, content, thread_id, creator_id, sent_at FROM messages WHERE id=:message_id AND is_visible=True"
    result = db.session.execute(sql, {"message_id":message_id}).fetchone()
    if not result:
        return []
    return result

def edit(message_id, content):
    sql = "UPDATE messages SET content=:content WHERE id=:message_id"
    db.session.execute(sql, {"message_id":message_id, "content":content})
    db.session.commit()

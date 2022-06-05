from app import db
import users

def create(subject, topic_id, message):
    if users.user_id() == 0:
        return False
    try:
        sql = "INSERT INTO threads (subject, topic_id, creator_id, is_visible) VALUES (:subject,:topic_id,:creator_id, True) RETURNING id"
        result = db.session.execute(sql, {"subject":subject, "topic_id":topic_id, "creator_id":users.user_id()})
        thread_id=result.fetchone()[0]
        if message:
            sql2 = "INSERT INTO messages (content, thread_id, creator_id, is_visible, sent_at) VALUES (:content,:thread_id,:creator_id, True, NOW())"
            db.session.execute(sql2, {"content":message, "thread_id":thread_id, "creator_id":users.user_id()})
        db.session.commit()
        return True
    except:
        return False

def list_threads(topic_id):
    sql = "SELECT id, subject, creator_id FROM threads WHERE topic_id=:topic_id AND is_visible = True"
    result = db.session.execute(sql, {"topic_id":topic_id})
    return result.fetchall()

def get_thread(thread_id):
    if users.user_id() == 0:
        return []
    sql = "SELECT id, subject, topic_id FROM threads WHERE id=:thread_id AND is_visible=True"
    result = db.session.execute(sql, {"thread_id":thread_id}).fetchone()
    if not result:
        return []
    return result

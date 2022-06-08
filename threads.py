from app import db
import users

def create(subject, topic_id, message):
    if users.user_id() == 0:
        return False
    try:
        if message:
            sql = "INSERT INTO threads (subject, topic_id, creator_id, is_visible, count_messages, latest_message) VALUES (:subject,:topic_id,:creator_id, True, 1, NOW()) RETURNING id, latest_message"
            result = db.session.execute(sql, {"subject":subject, "topic_id":topic_id, "creator_id":users.user_id()})
            row = result.fetchone()
            thread_id = row[0]
            sent_at = row[1]
            sql2 = "INSERT INTO messages (content, thread_id, creator_id, is_visible, sent_at) VALUES (:content,:thread_id,:creator_id, True,:sent_at)"
            db.session.execute(sql2, {"content":message, "thread_id":thread_id, "creator_id":users.user_id(), "sent_at":sent_at})
            sql3 = "UPDATE topics SET count_threads=count_threads+1, count_messages=count_messages+1, latest_message=:sent_at WHERE id=:topic_id"
            db.session.execute(sql3, {"topic_id":topic_id, "sent_at":sent_at})
            db.session.commit()
        else:
            sql = "INSERT INTO threads (subject, topic_id, creator_id, is_visible, count_messages) VALUES (:subject,:topic_id,:creator_id, True, 0)"
            db.session.execute(sql, {"subject":subject, "topic_id":topic_id, "creator_id":users.user_id()})
            sql2 = "UPDATE topics SET count_threads=count_threads+1 WHERE id=:topic_id"
            db.session.execute(sql2, {"topic_id":topic_id})
            db.session.commit()
        return True
    except:
        return False

def list_threads(topic_id):
    sql = "SELECT id, subject, creator_id, count_messages, latest_message FROM threads WHERE topic_id=:topic_id AND is_visible = True"
    result = db.session.execute(sql, {"topic_id":topic_id})
    return result.fetchall()

def get_thread(thread_id):
    if users.user_id() == 0:
        return []
    sql = "SELECT id, subject, topic_id, creator_id, count_messages, latest_message FROM threads WHERE id=:thread_id AND is_visible=True"
    result = db.session.execute(sql, {"thread_id":thread_id}).fetchone()
    if not result:
        return []
    return result

def edit(thread_id, subject):
    sql = "UPDATE threads SET subject=:subject WHERE id=:thread_id RETURNING id, subject, topic_id, creator_id"
    result = db.session.execute(sql, {"thread_id":thread_id, "subject":subject})
    db.session.commit()
    return result.fetchone()

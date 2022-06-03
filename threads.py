from app import db
import users, topics

def create(name, topic_id):
    if not topics.user_has_access(topic_id):
        return False
    return True

def list_threads(topic_id):
    sql = "SELECT id, subject, creator_id FROM threads WHERE topic_id=:topic_id AND is_visible = True"
    result = db.session.execute(sql, {"topic_id":topic_id})
    return result.fetchall()

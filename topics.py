from app import db
import users

def create(name, is_hidden, have_access):
    if users.user_id() == 0 or not users.is_admin():
        return False
    try:
        sql = """
                INSERT INTO topics (name, is_visible, is_hidden, count_messages, count_threads) 
                VALUES (:name,true,:is_hidden, 0, 0) 
                RETURNING id"""
        result = db.session.execute(sql, {"name":name, "is_hidden":is_hidden})
        topic_id = result.fetchone()[0]
        if is_hidden:
            for user_id in have_access:
                sql = "INSERT INTO topic_access (topic_id, user_id) VALUES (:topic_id, :user_id)"
                db.session.execute(sql, {"topic_id":topic_id, "user_id":user_id})
        db.session.commit()
        return True
    except:
        return False

def list_topics():
    if users.is_admin():
        sql = """
            SELECT id, name, count_threads, count_messages, latest_message 
            FROM topics 
            WHERE is_visible=True 
            ORDER BY name"""
        result = db.session.execute(sql)
    else:
        sql = """
            SELECT t.id, t.name, t.count_threads, t.count_messages, t.latest_message 
            FROM topics t LEFT JOIN topic_access ta ON t.id = ta.topic_id 
            WHERE is_visible=True AND (is_hidden = False OR ta.user_id = :user_id) 
            ORDER BY t.name"""
        result = db.session.execute(sql, {"user_id":users.user_id()})
    return result.fetchall()

def get_users_and_access_rights(topic_id):
    sql = """
            SELECT DISTINCT u.id, u.username, t2.user_id AS has_access 
            FROM users u LEFT JOIN (SELECT user_id FROM topic_access WHERE topic_id=:topic_id) t2 
                ON u.id = t2.user_id 
            ORDER BY u.username"""
    result = db.session.execute(sql, {"topic_id":topic_id})
    return result.fetchall()

def edit(topic_id, name, is_hidden, revoke_access, grant_access):
    sql = "UPDATE topics SET name=:name, is_hidden=:is_hidden WHERE id=:topic_id"
    db.session.execute(sql, {"topic_id":topic_id, "name":name, "is_hidden":is_hidden})
    if revoke_access:
        for user_id in revoke_access:
            sql = "DELETE FROM topic_access WHERE topic_id=:topic_id AND user_id=:user_id"
            db.session.execute(sql, {"topic_id":topic_id, "user_id":user_id})
    if grant_access:
        for user_id in grant_access:
            sql = "INSERT INTO topic_access (topic_id, user_id) VALUES (:topic_id, :user_id)"
            db.session.execute(sql, {"topic_id":topic_id, "user_id":user_id})
    db.session.commit()

def topic_exists(topic_id):
    sql = "SELECT id FROM topics where id=:topic_id AND is_visible=True"
    result = db.session.execute(sql, {"topic_id":topic_id})
    if result.fetchone():
        return True
    return False

def get_topic_if_user_has_access(topic_id):
    if users.user_id() == 0:
        return []
    sql = """   SELECT id, name, is_hidden, count_threads, count_messages, latest_message 
                FROM topics 
                WHERE id=:topic_id AND is_visible=True"""
    result1 = db.session.execute(sql, {"topic_id":topic_id}).fetchone()
    if not result1:
        return []
    if users.is_admin():
        return result1
    if result1["is_hidden"]==False:
        return result1
    sql = "SELECT user_id FROM topic_access WHERE topic_id=:topic_id AND user_id=:user_id"
    result2 = db.session.execute(sql, {"topic_id":topic_id, "user_id":users.user_id()}).fetchone()
    if result2:
        return result1
    return []

def delete(topic_id):
    sql = """   UPDATE topics 
                SET is_visible=False, count_threads=0, count_messages=0, latest_message=NULL 
                WHERE id=:topic_id"""
    db.session.execute(sql, {"topic_id":topic_id})
    
    sql2 = """  UPDATE threads 
                SET count_messages=0, latest_message=NULL, is_visible=False 
                WHERE topic_id=:topic_id"""
    db.session.execute(sql2, {"topic_id":topic_id})

    sql3 = """  UPDATE messages 
                SET is_visible=False 
                WHERE thread_id 
                    IN (
                        SELECT id 
                        FROM threads 
                        WHERE topic_id=:topic_id)
            """
    db.session.execute(sql3, {"topic_id":topic_id})

    db.session.commit()

def search(query):
    if users.is_admin():
        sql = """   SELECT id, name, count_threads, count_messages, latest_message 
                    FROM topics 
                    WHERE is_visible=True AND UPPER(name) LIKE UPPER(:query) ORDER BY name"""
        result = db.session.execute(sql, {"query":"%"+query+"%"})
    else:
        sql = """
            SELECT  t.id, t.name, t.count_threads, t.count_messages, t.latest_message 
            FROM topics t 
                LEFT JOIN topic_access ta 
                ON t.id = ta.topic_id 
            WHERE 
                is_visible=True AND 
                (is_hidden = False OR ta.user_id = :user_id) AND 
                UPPER(name) LIKE UPPER(:query) 
            ORDER BY t.name"""
        result = db.session.execute(sql, {"user_id":users.user_id(), "query":"%"+query+"%"})
    return result.fetchall()

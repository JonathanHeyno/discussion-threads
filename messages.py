from app import db
import users

def create(thread_id, content):
    if users.user_id() == 0:
        return False
    try:
        sql = """
            INSERT INTO messages (
                content, thread_id, creator_id, is_visible, sent_at) 
            VALUES (:content,:thread_id,:creator_id, True, NOW()) 
            RETURNING sent_at"""
        result = db.session.execute(sql, {"content":content, "thread_id":thread_id, "creator_id":users.user_id()})
        sent_at = result.fetchone()[0]
        sql2 = """  UPDATE threads 
                    SET count_messages=count_messages+1, latest_message=:sent_at 
                    WHERE id=:thread_id 
                    RETURNING topic_id"""
        result2 = db.session.execute(sql2, {"thread_id":thread_id, "sent_at":sent_at})
        topic_id = result2.fetchone()[0]
        sql3 = """  UPDATE topics 
                    SET count_messages=count_messages+1, latest_message=:sent_at 
                    WHERE id=:topic_id"""
        db.session.execute(sql3, {"topic_id":topic_id, "sent_at":sent_at})
        db.session.commit()
        return True
    except:
        return False

def list_messages(thread_id):
    sql = """
        SELECT m.id, m.content, m.creator_id, m.sent_at, u.username, 
            CASE WHEN m.creator_id=:user_id THEN True ELSE False END AS is_creator 
        FROM messages m, users u 
        WHERE m.thread_id=:thread_id AND m.is_visible = True AND m.creator_id=u.id 
        ORDER BY m.sent_at DESC"""
    result = db.session.execute(sql, {"thread_id":thread_id, "user_id":users.user_id()})
    return result.fetchall()

def get_message(message_id):
    if users.user_id() == 0:
        return []
    sql = """   SELECT id, content, thread_id, creator_id, sent_at 
                FROM messages 
                WHERE id=:message_id AND is_visible=True"""
    result = db.session.execute(sql, {"message_id":message_id}).fetchone()
    if not result:
        return []
    return result

def edit(message_id, content):
    sql = "UPDATE messages SET content=:content WHERE id=:message_id"
    db.session.execute(sql, {"message_id":message_id, "content":content})
    db.session.commit()

def delete(message_id):
    sql = "UPDATE messages SET is_visible=False WHERE id=:message_id RETURNING thread_id, sent_at"
    result = db.session.execute(sql, {"message_id":message_id})
    row = result.fetchone()
    thread_id = row[0]
    sent_at = row[1]

    sql2 = """
    UPDATE threads SET count_messages=count_messages-1, latest_message=
        CASE 
            WHEN latest_message =:sent_at THEN (
                SELECT MAX(sent_at) 
                FROM messages 
                WHERE thread_id=:thread_id AND is_visible=True)
            ELSE 
                latest_message 
        END
    WHERE id=:thread_id RETURNING id, subject, topic_id, creator_id, count_messages, latest_message
    """
    result2 = db.session.execute(sql2, {"thread_id":thread_id, "sent_at":sent_at})
    thread = result2.fetchone()


    sql3 = """
    UPDATE topics SET count_messages=count_messages-1, latest_message=
        CASE 
            WHEN latest_message =:sent_at 
                THEN (
                    SELECT MAX(latest_message) 
                    FROM threads 
                    WHERE topic_id=:topic_id AND is_visible=True)
            ELSE 
                latest_message 
        END
    WHERE id=:topic_id RETURNING id, name, is_hidden, count_threads, count_messages, latest_message
    """
    result3 = db.session.execute(sql3, {"topic_id":thread["topic_id"], "sent_at":sent_at})
    topic = result3.fetchone()

    db.session.commit()
    return topic, thread

def search(query):
    if users.is_admin():
        sql = """
        SELECT  m.id, m.content, m.thread_id, m.creator_id, m.sent_at, u.username, 
                CASE WHEN m.creator_id=:user_id THEN True ELSE False END AS is_creator 
        FROM messages m, users u 
        WHERE m.is_visible = True AND m.creator_id=u.id AND UPPER(content) LIKE UPPER(:query) 
        ORDER BY m.sent_at DESC
        """
        result = db.session.execute(sql, {"user_id":users.user_id(), "query":"%"+query+"%"})
    else:
        sql = """
        SELECT  m.id, m.content, m.thread_id, m.creator_id, m.sent_at, u.username, 
                CASE WHEN m.creator_id=:user_id THEN True ELSE False END AS is_creator 
        FROM 
            messages m, 
            threads, 
            (
                SELECT t.id 
                FROM topics t LEFT JOIN topic_access ta ON t.id = ta.topic_id 
                WHERE is_visible=True AND (is_hidden = False OR ta.user_id = :user_id) 
            ) AS allowed_topics, 
            users u 
        WHERE   UPPER(content) LIKE UPPER(:query) AND 
                m.is_visible=TRUE AND 
                m.thread_id=threads.id AND 
                threads.topic_id=allowed_topics.id AND
                m.creator_id=u.id
        ORDER BY m.sent_at DESC
        """
        result = db.session.execute(sql, {"user_id":users.user_id(), "query":"%"+query+"%"})
    return result.fetchall()

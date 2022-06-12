from app import db
import users

def create(subject, topic_id, message):
    if users.user_id() == 0:
        return False
    try:
        if message:
            sql = """
                INSERT INTO threads (
                    subject, 
                    topic_id, 
                    creator_id, 
                    is_visible, 
                    count_messages, 
                    latest_message) 
                VALUES (:subject,:topic_id,:creator_id, True, 1, NOW()) 
                RETURNING id, latest_message
                """
            result = db.session.execute(sql, {"subject":subject, "topic_id":topic_id, "creator_id":users.user_id()})
            row = result.fetchone()
            thread_id = row[0]
            sent_at = row[1]
            sql2 = """  INSERT INTO messages (content, thread_id, creator_id, is_visible, sent_at) 
                        VALUES (:content,:thread_id,:creator_id, True,:sent_at)"""
            db.session.execute(sql2, {"content":message, "thread_id":thread_id, "creator_id":users.user_id(), "sent_at":sent_at})
            sql3 = """  UPDATE topics 
                        SET count_threads=count_threads+1, 
                            count_messages=count_messages+1, 
                            latest_message=:sent_at 
                        WHERE id=:topic_id"""
            db.session.execute(sql3, {"topic_id":topic_id, "sent_at":sent_at})
            db.session.commit()
        else:
            sql = """   INSERT INTO threads (subject, topic_id, creator_id, is_visible, count_messages) 
                        VALUES (:subject,:topic_id,:creator_id, True, 0)"""
            db.session.execute(sql, {"subject":subject, "topic_id":topic_id, "creator_id":users.user_id()})
            sql2 = "UPDATE topics SET count_threads=count_threads+1 WHERE id=:topic_id"
            db.session.execute(sql2, {"topic_id":topic_id})
            db.session.commit()
        return True
    except:
        return False

def list_threads(topic_id):
    sql =   """
            SELECT id, subject, creator_id, count_messages, latest_message 
            FROM threads WHERE topic_id=:topic_id AND is_visible = True
            """
    result = db.session.execute(sql, {"topic_id":topic_id})
    return result.fetchall()

def get_thread(thread_id):
    if users.user_id() == 0:
        return []
    sql = """
        SELECT id, subject, topic_id, creator_id, count_messages, latest_message 
        FROM threads WHERE id=:thread_id AND is_visible=True
        """
    result = db.session.execute(sql, {"thread_id":thread_id}).fetchone()
    if not result:
        return []
    return result

def edit(thread_id, subject):
    sql = """   
            UPDATE threads 
            SET subject=:subject 
            WHERE id=:thread_id 
            RETURNING id, subject, topic_id, creator_id
            """
    result = db.session.execute(sql, {"thread_id":thread_id, "subject":subject})
    db.session.commit()
    return result.fetchone()

def delete(thread_id):
    sql = """
        UPDATE threads 
        SET is_visible=False 
        WHERE id=:thread_id 
        RETURNING topic_id, count_messages, latest_message
        """
    result = db.session.execute(sql, {"thread_id":thread_id})
    row = result.fetchone()
    topic_id = row[0]
    count_messages = row[1]
    latest_message = row[2]
    
    sql2="""UPDATE messages SET is_visible=False WHERE thread_id=:thread_id"""
    db.session.execute(sql2, {"thread_id":thread_id})

    sql3 = "UPDATE threads SET count_messages=0, latest_message=NULL WHERE id=:thread_id"
    db.session.execute(sql3, {"thread_id":thread_id})


    sql4 = """
    UPDATE topics SET count_threads=count_threads-1, count_messages=count_messages-:count_messages, latest_message=
        CASE 
            WHEN latest_message =:latest_message THEN (
                SELECT MAX(sent_at) 
                FROM messages m LEFT JOIN threads t ON m.thread_id=t.id 
                WHERE t.topic_id=:topic_id AND m.is_visible=True)
            ELSE 
                latest_message 
        END
    WHERE id=:topic_id RETURNING id, name, is_hidden, count_threads, count_messages, latest_message
    """
    result4 = db.session.execute(sql4, {"topic_id":topic_id, "count_messages":count_messages, "latest_message":latest_message})
    topic = result4.fetchone()

    db.session.commit()
    return topic

def search(query):
    if users.is_admin():
        sql = """
                SELECT id, subject, creator_id, count_messages, latest_message 
                FROM threads 
                WHERE is_visible = True AND UPPER(subject) LIKE UPPER(:query)"""
        result = db.session.execute(sql, {"query":"%"+query+"%"})
    else:
        sql = """
        SELECT id, subject, creator_id, count_messages, latest_message 
        FROM 
            threads t, 
            (
                SELECT topics.id AS topic_id
                FROM topics 
                LEFT JOIN topic_access ta 
                ON topics.id = ta.topic_id 
                WHERE topics.is_visible=TRUE AND (topics.is_hidden=FALSE OR ta.user_id = :user_id) 
            ) AS t2
        WHERE t.topic_id = t2.topic_id AND t.is_visible=TRUE AND UPPER(t.subject) LIKE UPPER(:query)
        """
        result = db.session.execute(sql, {"user_id":users.user_id(), "query":"%"+query+"%"})

    return result.fetchall()

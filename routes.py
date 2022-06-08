from app import app
from flask import render_template, request, redirect
import users, topics, threads, messages
from werkzeug.exceptions import abort

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/topics")
        else:
            return render_template("login.html", login_message="Incorrect username or password")

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    password2 = request.form["password2"]
    is_admin = False
    if request.form.getlist("is_admin"):
        is_admin = True
    register_message = users.register(username, password, password2, is_admin)
    if register_message == "OK":
        return redirect("/topics")
    else:
        return render_template("login.html", register_message=register_message)

@app.route("/topics", methods=["GET", "POST"])
def show_topics():
    if users.user_id() == 0:
        return render_template("login.html", login_message="Not logged in")
    if request.method == "GET":
        return render_template("topics.html", is_admin=users.is_admin(), topic_list=topics.list_topics())
    if request.method == "POST":
        return redirect("/create_topic")

@app.route("/get_topic_for_editing/<int:topic_id>", methods=["POST"])
def get_topic_for_editing(topic_id):
    return redirect("/edit_topic/"+str(topic_id))

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")


@app.route("/create_topic", methods=["GET", "POST"])
def create_topic():
    if users.user_id() == 0:
        return render_template("login.html", login_message="Not logged in")
    if not users.is_admin():
        abort(401, description="Not an administrator")
    if request.method == "GET":
        userslist=users.get_users()
        return render_template("create_topic.html", users=userslist)
    if request.method == "POST":
        name = request.form["name"]
        is_hidden = False
        if request.form.getlist("is_hidden"):
            is_hidden = True
        have_access = request.form.getlist("have_access")
        if topics.create(name, is_hidden, have_access):
            return render_template("topics.html", is_admin=users.is_admin(), topic_list=topics.list_topics(), message="Topic created")
    userslist=users.get_users()
    return render_template("create_topic.html", message="Could not create topic", users=userslist)

@app.route("/edit_topic/<int:topic_id>", methods=["GET", "POST"])
def edit_topic(topic_id):
    if users.user_id() == 0:
        return render_template("login.html", login_message="Not logged in")
    if not users.is_admin():
        abort(403, description="Not an administrator")
    topic = topics.get_topic_if_user_has_access(topic_id)
    if not topic:
        abort(404, description="Topic does not exist")
    if request.method == "GET":
        return render_template("edit_topic.html", topic=topic,
        user_accesses=topics.get_users_and_access_rights(topic_id))
    if request.method == "POST":
        name = request.form["name"]
        is_hidden = False
        if request.form.getlist("is_hidden"):
            is_hidden = True
        revoke_access = request.form.getlist("revoke_access")
        grant_access = request.form.getlist("grant_access")
        topics.edit(topic_id, name, is_hidden, revoke_access, grant_access)
        return render_template("topics.html", is_admin=users.is_admin(), topic_list=topics.list_topics(), message="Saved changes to topic")
    return render_template("topics.html", is_admin=users.is_admin(), topic_list=topics.list_topics(), message="Could not save changes to topic")


@app.route("/topic/<int:topic_id>", methods=["GET", "POST"])
def topic(topic_id):
    if users.user_id() == 0:
        return render_template("login.html", login_message="Not logged in")
    if request.method == "GET":
        topic = topics.get_topic_if_user_has_access(topic_id)
        if not topic:
            abort(404, description="Access to topic denied or topic does not exist")
        return render_template("topic.html", topic=topic, threads=threads.list_threads(topic_id))
    if request.method == "POST":
        return redirect("/create_thread/"+str(topic_id))

@app.route("/create_thread/<int:topic_id>", methods=["GET", "POST"])
def create_thread(topic_id):
    if users.user_id() == 0:
        return render_template("login.html", login_message="Not logged in")
    topic = topics.get_topic_if_user_has_access(topic_id)
    if not topic:
        abort(404, description="Access to topic denied or topic does not exist")
    if request.method == "GET":
        return render_template("create_thread.html", topic=topic)
    if request.method == "POST":
        subject = request.form["subject"]
        message = request.form["message"]
        if threads.create(subject, topic_id, message):
            return render_template("topic.html", topic=topic, threads=threads.list_threads(topic_id), message="Thread created")
    return render_template("create_thread.html", topic=topic, message="Could not create thread")

@app.route("/thread/<int:thread_id>", methods=["GET", "POST"])
def thread(thread_id):
    if users.user_id() == 0:
        return render_template("login.html", login_message="Not logged in")
    thread = threads.get_thread(thread_id)
    if not thread:
        abort(404, description="Thread does not exist")
    topic = topics.get_topic_if_user_has_access(thread["topic_id"])
    if not topic:
        abort(403, description="Access denied")
    if request.method == "GET":
        return render_template("thread.html", is_creator=thread["creator_id"]==users.user_id(), topic=topic, thread=thread, messages=messages.list_messages(thread_id))
    if request.method == "POST":
        content = request.form["content"]
        #if messages.new(content, thread_id):
        if messages.create(thread_id, content):
            return render_template("thread.html", is_creator=thread["creator_id"]==users.user_id(), topic=topic, thread=thread, messages=messages.list_messages(thread_id), message="Message sent")
        return render_template("thread.html", is_creator=thread["creator_id"]==users.user_id(), topic=topic, thread=thread, messages=messages.list_messages(thread_id), message="Could not send message")

@app.route("/get_thread_for_editing/<int:thread_id>", methods=["POST"])
def get_thread_for_editing(thread_id):
    return redirect("/edit_thread/"+str(thread_id))

@app.route("/edit_thread/<int:thread_id>", methods=["GET", "POST"])
def edit_thread(thread_id):
    if users.user_id() == 0:
        return render_template("login.html", login_message="Not logged in")
    thread = threads.get_thread(thread_id)
    if not thread:
        abort(404, description="Thread does not exist")
    if thread["creator_id"] != users.user_id():
        abort(403, description="Access denied")
    #topic = topics.get_topic_if_user_has_access(thread["topic_id"])
    #if not topic:
    #    abort(403, description="Access denied")
    if request.method == "GET":
        return render_template("edit_thread.html", thread=thread)
    if request.method == "POST":
        subject = request.form["subject"]
        thread = threads.edit(thread_id, subject)
        topic = topics.get_topic_if_user_has_access(thread["topic_id"])
        return render_template("thread.html", is_creator=thread["creator_id"]==users.user_id(), topic=topic, thread=thread, messages=messages.list_messages(thread_id), message="Changes saved")
    return render_template("edit_thread.html",  thread=thread, message="Could not save changes")

@app.route("/edit_message/<int:message_id>", methods=["GET", "POST"])
def edit_message(message_id):
    if users.user_id() == 0:
        return render_template("login.html", login_message="Not logged in")
    message = messages.get_message(message_id)
    if not message:
        abort(404, description="Message does not exist")
    if message["creator_id"] != users.user_id():
        abort(403, description="Access denied")
    if request.method == "GET":
        return render_template("edit_message.html", message=message)
    if request.method == "POST":
        content = request.form["content"]
        messages.edit(message_id, content)
        thread = threads.get_thread(message["thread_id"])
        topic = topics.get_topic_if_user_has_access(thread["topic_id"])
        return render_template("thread.html", is_creator=thread["creator_id"]==users.user_id(), topic=topic, thread=thread, messages=messages.list_messages(message["thread_id"]), message="Saved message")
    return render_template("edit_message.html", message=message, error="Could not save changes")

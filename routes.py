from app import app
from flask import render_template, request, redirect, session
import users, topics, threads
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
    userslist=users.get_users()
    if request.method == "GET":
        return render_template("create_topic.html", users=userslist)
    if request.method == "POST":
        name = request.form["name"]
        is_hidden = False
        if request.form.getlist("is_hidden"):
            is_hidden = True
        have_access = request.form.getlist("have_access")
        if topics.create(name, is_hidden, have_access):
            return render_template("topics.html", is_admin=users.is_admin(), topic_list=topics.list_topics(), message="Topic created")
    return render_template("create_topic.html", message="Could not create topic", users=userslist)

@app.route("/edit_topic/<int:topic_id>", methods=["GET", "POST"])
def edit_topic(topic_id):
    if users.user_id() == 0:
        return render_template("login.html", login_message="Not logged in")
    if not users.is_admin():
        abort(401, description="Not an administrator")
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
    topic = topics.get_topic_if_user_has_access(topic_id)
    if not topic:
        abort(401, description="Access to topic denied or topic does not exist")
    if request.method == "GET":
        return render_template("topic.html", topic=topic, threads=threads.list_threads(topic_id))
    if request.method == "POST":
        return redirect("/create_thread")

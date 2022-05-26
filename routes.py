from app import app
from flask import render_template, request, redirect, session
#import messages, users
import users
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
    if register_message == 'OK':
        return redirect("/topics")
    else:
        return render_template("login.html", register_message=register_message)

@app.route("/topics")
def topics():
    return render_template("topics.html", is_admin=session["is_admin"])

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")



#@app.route("/")
#def index():
#    list = messages.get_list()
#    return render_template("index.html", count=len(list), messages=list)

'''
@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/send", methods=["POST"])
def send():
    content = request.form["content"]
    if messages.send(content):
        return redirect("/")
    else:
        return render_template("error.html", message="Viestin lähetys ei onnistunut")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/")
        else:
            return render_template("error.html", message="Väärä tunnus tai salasana")

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return render_template("error.html", message="Salasanat eroavat")
        if users.register(username, password1):
            return redirect("/")
        else:
            return render_template("error.html", message="Rekisteröinti ei onnistunut")
'''

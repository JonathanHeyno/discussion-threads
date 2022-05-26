from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from os import getenv

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
csrf = CSRFProtect(app)
db = SQLAlchemy(app)

import routes

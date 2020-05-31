import os
from flask import Flask, session, render_template, jsonify, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *

app = Flask(__name__)
app.secret_key = 'sitting out on your house watching hardcore UFOs'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# ## Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))
# db = scoped_session(sessionmaker(bind=engine))
# # db.init_app(app)

def getExistingUser(username):
    existingUser = AppUser.query.filter_by(username=username).first()
    return existingUser


@app.route("/")
def index():
    if hasattr(session,"user_id"):
        return render_template("search.html")
    else:
        return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        username = request.form.get("loginUsername")
        password = request.form.get("loginPassword")
        user = getExistingUser(username)
        if not user:
            return render_template("index.html", message="User not registered.")
        else:
            if(user.username == username and user.password == password):
                session["user_id"] = user.id
                print('logging in user: ')
                print(session["user_id"])
                return render_template("search.html")
            else:
                return render_template("index.html", message="Incorrect username or password.")
    else:
        if session.get("user_id", False):
            session.pop('user_id', None)
            return render_template("index.html", message="Logged out successfully.")
        else:
            return render_template("index.html", message="User already logged out.")

@app.route("/logout")
def logout():
    if session.get("user_id", False):
        session.pop('user_id', None)
        return render_template("index.html", message="Logged out successfully.")
    else:
        return render_template("index.html", message="User already logged out.")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        username = request.form.get("registerUsername")
        password = request.form.get("registerPassword")
        existingUser = getExistingUser(username)
        if not existingUser:
            newUser = AppUser(username=username, password=password)
            db.session.add(newUser)
            db.session.commit() # commit user
            return render_template("register.html", message="User registered succesfully.")
        else:
            return render_template("index.html", message="User already registered, please log in.")
    else:
        return render_template("register.html")

# @app.route("/login", methods=["POST"])
# def index():
#     # some code
#     return render_template("search")

#@app.search("/search", methods=["POST"])

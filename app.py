import os
from flask import Flask, session, render_template, jsonify, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine, or_
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

def userLoggedIn(session):
    if session.get("user_id", False):
        return True
    else:
        return False

@app.route("/")
def index():
    if userLoggedIn(session):
        return render_template("search.html")
    else:
        return render_template("index.html", message = "Please log in")

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
                return redirect(url_for("index"))
            else:
                return render_template("index.html", message="Incorrect username or password.")
    else:
        if userLoggedIn(session):
            return redirect(url_for("index"))
        else:
            return render_template("index.html")

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
            return render_template("index.html", message="User registered succesfully. Please log in.")
        else:
            return render_template("index.html", message="User already registered. Please log in.")
    else:
        return render_template("register.html")

@app.route("/search", methods=['GET', 'POST'])
def search():
    # POST
    if request.method=='POST':
        searchTerm = request.form.get("bookSearchTerm")
        ## parse search term into words
        ## query database
        searchResults = Book.query.order_by(Book.title).join(Author, Book.authorid==Author.id).\
                                    add_columns(Book.id, Book.isbn, Book.title, Book.year,Author.name.label("author")).\
                                    filter(or_(Book.title.ilike('%'+searchTerm+'%'),Book.isbn.ilike('%'+searchTerm+'%'), Author.name.ilike('%'+searchTerm+'%')))
        resultCount = searchResults.count()
        if(resultCount==0):
            resultString = 'No results for '
        elif(resultCount==1):
            resultString = '1 result for '
        else:
            resultString = str(resultCount) + ' results for '
        return render_template("results.html", searchTerm=searchTerm, searchResults=searchResults, resultCount=resultString)
    # GET
    else:
        return render_template("results.html")


@app.route("/book/<int:book_id>")
def book(book_id):
    book = Book.query.get(book_id)
    if book is None:
        return render_template("error.html", message="Book not found.")
    else:
        author = Author.query.get(book.authorid)
        reviews = Review.query.filter_by(bookid=book.id)
        return render_template("book.html", book=book, author=author, reviews=reviews)


@app.route("/review/<int:book_id>", methods=['POST'])
def review(book_id):
    reviewContent = request.form.get("reviewContent")
    reviewRating = request.form.get("reviewRating")
    appuserid = session["user_id"]
    existingReview = Review.query.filter(Review.bookid == book_id, Review.appuserid == appuserid).first()
    if not existingReview:
        newReview = Review(bookid=book_id, appuserid=appuserid, rating=reviewRating, content=reviewContent)
        db.session.add(newReview)
        db.session.commit() # commit user
        message = "Review submitted successfully"
    else:
        message = "You have already reviewed this book"
    book = Book.query.get(book_id)
    author = Author.query.get(book.authorid)
    reviews = Review.query.filter_by(bookid=book.id)
    return render_template("book.html", message=message, book=book, author=author, reviews=reviews)

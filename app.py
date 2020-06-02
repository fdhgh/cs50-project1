import os
from flask import Flask, session, render_template, jsonify, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
import requests
from statistics import mean


# Check for goodreads api key environment variable
if not os.getenv("GOODREADS_API_KEY"):
    raise RuntimeError("GOODREADS_API_KEY is not set")
# goodreads API key
grKey=os.getenv("GOODREADS_API_KEY")
grBaseUrl="https://www.goodreads.com/book/"

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

def getBookDetails(book):
    author = Author.query.get(book.authorid)
    reviews = Review.query.join(AppUser, Review.appuserid==AppUser.id).\
                            add_columns(Review.content,Review.rating,AppUser.username).\
                            filter(Review.bookid==book.id)
    return author, reviews

def getCurrentUser(session):
    if session.get("user_id", False):
        user = AppUser.query.get(session["user_id"])
        return user
    else:
        return False

def loginUser(session,userid):
    session["user_id"] = userid
    return None

def goodreads(book):
    res = requests.get((grBaseUrl+"review_counts.json"), params={"key": grKey, "isbns": book.isbn})
    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")
    data = res.json()
    ratings_count = data["books"][0]["work_ratings_count"]
    avg_rating =data["books"][0]["average_rating"]
    return ratings_count,avg_rating

@app.before_request
def before_request():
    if not session.get("user_id", False) and request.endpoint not in ['login','register']:
        return redirect(url_for('login'))

@app.route("/")
def index():
    return render_template("search.html")

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
                loginUser(session,user.id)
                return redirect(url_for("index"))
            else:
                return render_template("index.html", message="Incorrect username or password.")
    else:
        currentUser = getCurrentUser(session)
        if currentUser:
            return redirect(url_for("index"))
        else:
            message = "You are not currently logged in"
            return render_template("index.html", message=message)

@app.route("/logout")
def logout():
    currentUser = getCurrentUser(session)
    if currentUser:
        session.pop('user_id', None)
        return render_template("index.html", message="Logged out successfully.")

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
            currentUser = getExistingUser(username)
            loginUser(session, currentUser.id)
            #return render_template("index.html", message="User registered succesfully. Please log in.")
            return redirect(url_for("index"))
        else:
            return render_template("register.html", message="Username already taken.")
    else:
        currentUser = getCurrentUser(session)
        if currentUser:
            return redirect(url_for("index"))
        else:
            return render_template("register.html")

@app.route("/search", methods=['GET', 'POST'])
def search():
    # POST
    if request.method=='POST':
        searchTerm = request.form.get("bookSearchTerm")
        ## query database
        searchResults = Book.query.order_by(Book.title).\
                                    join(Author, Book.authorid==Author.id).\
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
        thisPage=url_for("search")
        returnToPage = "Search"
        return render_template("error.html", message="Book not found.", prevPage=thisPage, returnToPage=returnToPage)
    else:
        author, reviews = getBookDetails(book)
        ratings_count,avg_rating = goodreads(book)
        print(type(reviews))
        return render_template("book.html", book=book, author=author, reviews=reviews, ratings_count=ratings_count,avg_rating=avg_rating)


@app.route("/review/<int:book_id>", methods=['POST'])
def review(book_id):
    book = Book.query.get(book_id)
    thisPage=url_for("book", book_id=book_id)
    returnToPage = "previous page"
    reviewContent = request.form.get("reviewContent")
    reviewRating = request.form.get("reviewRating")
    appuserid = session["user_id"]

    existingReview = Review.query.filter(Review.bookid == book.id, Review.appuserid == appuserid).first()
    if not existingReview:
        if not reviewContent:
            message = "Review must contain some text"
            return render_template('error.html',message=message,prevPage=thisPage,returnToPage=returnToPage)
        else:
            book.add_review(appuserid, reviewRating, reviewContent)
            return redirect(thisPage)
    else:
        message = "You have already reviewed this book"
        return render_template('error.html',message=message,prevPage=thisPage,returnToPage=returnToPage)

@app.route("/api/<isbn>", methods=['GET'])
def getIsbn(isbn):
    # Make sure book exists.
    book = Book.query.filter_by(isbn=isbn).first()
    if book is None:
        return jsonify({"error": "Book not found"}), 404

    author, reviews = getBookDetails(book)

    # count reviews
    review_count = 0
    scores=[]
    for review in reviews:
        review_count +=1
        scores.append(review.rating)

    average_score = mean(scores)

    return jsonify({
            "title": book.title,
            "author": author.name,
            "year": book.year,
            "isbn": book.isbn,
            "review_count": review_count,
            "average_score": average_score
        })

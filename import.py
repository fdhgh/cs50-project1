import csv
import os

from flask import Flask, render_template, request
from models import *

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def getExistingAuthor(authorName):
    existingAuthor = Author.query.filter_by(name=authorName).limit(1).all()
    return existingAuthor

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    next(reader, None)  # skip the headers
    bookData = list(reader)

    ## import authors
    for isbn, title, authorName, year in bookData:
        existingAuthor = getExistingAuthor(authorName)
        if not existingAuthor:
            newAuthor = Author(name=authorName) # add new author
            db.session.add(newAuthor)
            print(f"Added author {authorName}.")
        # else:
        #     print(f"Author {authorName} already exists")
    db.session.commit() # commit authors

    authors = Author.query.all()
    ## import books
    for isbn, title, authorName, year in bookData:
        existingAuthor = [a.id for a in authors if a.name == authorName]
        if not existingAuthor:
            raise RuntimeError("Author not imported") # author does not exist error
        else:
            authorid = existingAuthor[0]
        book = Book(isbn=isbn,title=title,authorid=authorid,year=year)
        db.session.add(book)
        print(f"Added book with isbn {isbn} named {title} by {authorName} published {year}.")
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        main()


#
# print("SQLAlchemy version: " + sqlalchemy.__version__)
#
# dburl = os.getenv("DATABASE_URL")
#
# # Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))
# db = scoped_session(sessionmaker(bind=engine))
#
# with engine.connect() as con:
#     rs = con.execute(sqlcmdstring)
#
# sqlcmdstring = "put some sql commands here"

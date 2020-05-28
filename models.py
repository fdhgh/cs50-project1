from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = "book"
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    authorId = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)
    year = db.Column(db.Integer, nullable=False)

class Author(db.Model):
    __tablename__ = "author"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,unique=True, nullable=False)

class AppUser(db.Model):
    __tablename__ = "appUser"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String,unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

class Review(db.Model):
    __tablename__ = "review"
    id = db.Column(db.Integer, primary_key=True)
    bookId = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    appUserId = db.Column(db.Integer, db.ForeignKey("appUser.id"), nullable=False)
    rating = db.Column(db.Integer, db.CheckConstraint("rating>=1"),db.CheckConstraint("rating<=5"), nullable=False) # Ratings must be an integer from 1 - 5
    content = db.Column(db.String, db.CheckConstraint("length(content)<=10000"), nullable=False)
    __table_args__ = (db.UniqueConstraint('appUserId', 'bookId', name='_book_user_uc'), ) # Each user can only review each book once
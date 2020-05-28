import os

from flask import Flask, render_template, request
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
	authors = Author.query.all()

	authorName = "Jane Greeno"
	authorid = [x.id for x in authors if x.name == authorName]
	if not authorId:
		print('no author id')
	else: print(authorid[0])

if __name__ == "__main__":
	with app.app_context():
		main()

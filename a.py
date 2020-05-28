import csv
import os

from flask import Flask, render_template, request
from models import *

# Check for environment variable
if not os.getenv("DATABASE_URL"):
	raise RuntimeError("DATABASE_URL is not set")

print(os.getenv("DATABASE_URL"))
#     f = open("books.csv")
#     reader = csv.reader(f)
#     next(reader, None)  # skip the headers
#     # for isbn, title, bookAuthor, year in reader:
#     #
#     #     print(f"Added book with isbn {isbn} named {title} by {bookAuthor} published {year}.")

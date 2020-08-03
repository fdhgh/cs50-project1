# Project 1

Web Programming with Python and JavaScript

Book reviews website designed to meet the following requirements:

* Registration: Users should be able to register for the website, providing (at minimum) a username and password.
* Login: Users, once registered, should be able to log in to the website with their username and password.
* Logout: Logged in users should be able to log out of the site.
* Import: An import.py file should be created so that books can be imported to the database from a CSV.
* Search: Once a user has logged in, they should be taken to a page where they can search for a book. Users should be able to type in the ISBN number of a book, the title of a book, or the author of a book. After performing the search, the website should display a list of possible matching results, or some sort of message if there were no matches. If the user typed in only part of a title, ISBN, or author name, the search page should find matches for those as well.
* Book Page: When users click on a book from the results of the search page, they should be taken to a book page, with details about the book: its title, author, publication year, ISBN number, and any reviews that users have left for the book on the website.
* Review Submission: On the book page, users should be able to submit a review: consisting of a rating on a scale of 1 to 5, as well as a text component to the review where the user can write their opinion about a book. Users should not be able to submit multiple reviews for the same book.
* Goodreads Review Data: The book page should also display (if available) the average rating and number of ratings the work has received from Goodreads.
* API Access: If users make a GET request to the website’s /api/<isbn> route, where <isbn> is an ISBN number, your website should return a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score.

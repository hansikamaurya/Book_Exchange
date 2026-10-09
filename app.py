from flask import Flask, render_template, request, redirect, session, url_for
#so u dont have to add a flask. before calling a flask function everytime.
#flask- name of module; Flask- name of class/function
import mysql.connector
app = Flask(__name__)
app.secret_key = "book_exchange_project"

# connect to mysql
def get_db_connection():
    conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="H_sql_2026",
    database="book_exchange")
    return conn #sends connection back to where it was called from

# Welcome page
@app.route("/")# '/' :- homepage
def index():
    return render_template("index.html")

# Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            query = "INSERT INTO users (username, email) VALUES (%s, %s)"
            cursor.execute(query, (username, email))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for("login"))
        except mysql.connector.IntegrityError:
            cursor.close()
            conn.close()
            return "Username or email already exists!"
    return render_template("register.html")

#login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s",(username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session["username"] = username
            return redirect(url_for("home"))
        else:
            return "Username does not exist! Please register."
    return render_template("login.html")

# User homepage
@app.route("/home")
def home():
    if "username" not in session:#checking if username is logged in or not
        return redirect(url_for("login"))
    return render_template("home.html", username=session["username"]) 
    #passing the username over to the html page to be displayed by the jinja2 template in home.html


# Upload books
@app.route("/add", methods=["GET", "POST"])
def add_book():
    if "username" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """INSERT INTO books (title, author, owner)
            VALUES (%s, %s, %s)"""
        cursor.execute(
            query,
            (title, author, session["username"]))
            #title, author and username in session will be uploaded to db
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("books"))
    return render_template("add_book.html")

# Browse available books
@app.route("/books")
def books():
    if "username" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    #to return dict instead of tuples. accessing is easier
    query = """SELECT books.*, users.email 
        FROM books
        JOIN users ON books.owner = users.username
        WHERE books.status = 'Available'"""
    #selects all from books table, selects email from user table
    #books is the main table
    #join: 'on' is used with join to specify conditions
    #condition here: ownersfrom books table==username from users table. to make sure the correct email is displayed in the joint table
    #only displays books that are available
    cursor.execute(query)
    all_books = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("books.html", books=all_books)

# Logout
@app.route("/logout")
def logout():
    session.clear()#removes username in session
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
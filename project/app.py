import os
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    render_template,
    request,
    session,
    flash,
    redirect,
    url_for,
    abort,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError


basedir = Path(__file__).resolve().parent

# configuration
DATABASE = "flaskr.db"
SECRET_KEY = "change_me"
url = os.getenv("DATABASE_URL", f"sqlite:///{Path(basedir).joinpath(DATABASE)}")

if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URI = url
SQLALCHEMY_TRACK_MODIFICATIONS = False


# create and initialize a new Flask app
app = Flask(__name__)
# load the config
app.config.from_object(__name__)
# init sqlalchemy
db = SQLAlchemy(app)

from project import models


@app.route("/")
def index():
    """Searches the database for entries, then displays them."""
    entries = db.session.query(models.Post)
    return render_template("index.html", entries=entries)

from flask import request, abort

@app.route("/comment")
def comment_page():
    entry_id = request.args.get('entry_id', type=int)

    # Check if the entry_id is None or not found
    if entry_id is None:
        abort(404)  # Entry_id not found, you can customize the error handling

    # Retrieve the entry with the given entry_id from the database
    entry = db.session.query(models.Post).filter_by(id=entry_id).first()

    # Check if the entry exists
    if entry is None:
        abort(404)  # Entry not found, you can customize the error handling

    # Access the associated comments using the relationship defined in your models
    comments = entry.comments

    return render_template("comment.html", entry=entry, comments=comments)


@app.route("/post")
def post_page():
    """Searches the database for entries, th.schen displays them."""
    entries = db.session.query(models.Post)
    comments = db.session.query(models.Comment)
    username = session.get('username')
    return render_template("post.html", entries=entries, username=username, comments=comments)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not session.get("logged_in"):
        abort(401)

    userName = session.get('username')
    user = db.session.query(models.User).filter_by(uName=userName).first()
    #uFriends = db.session.query(models.User.friends).filter_by(uName=userName).first()
    #uFriends = user.friends
    #print(uFriends)
    return render_template("profile.html", user=user)

@app.route("/add_friend", methods=["POST"])
def add_friend():
    # Check if the user is logged in
    if not session.get("logged_in"):
        abort(401)

    # Get the current user's id from the session
    userName = session.get('username')

    # Get the friend's username from the form
    friend_username = request.form.get("fName")

    # Query the User table to find the current user and the friend
    user = db.session.query(models.User).filter_by(uName=userName).first()
    friend = db.session.query(models.User).filter_by(uName=friend_username).first()
    
    if friend:
        # Add the friend to the current user's friends list
        user.friends.append(friend)
        db.session.commit()
        # Flash a success message
        flash(f"You added {friend.uName} as a friend.")
    else:
        # Flash an error message
        flash(f"Friend not found. Please check the username.")

    # Redirect to the profile page
    return redirect(url_for("profile", user=userName))
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """User login/authentication/session management."""
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if the user with the provided username and password exists
        user = db.session.query(models.User).filter_by(uName=username, pWord=password).first()

        if user is None:
            error = "Invalid username or password"
        else:
            session['username'] = username
            session["logged_in"] = True
            flash("Logged in: " + username)
            return redirect(url_for("index"))

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    """User logout/authentication/session management."""
    session.pop("logged_in", None)
    flash("You were logged out")
    return redirect(url_for("login"))


@app.route("/create_user", methods=["GET", "POST"])
def create_user():
    """Adds new user"""
    error = None
    return render_template("cuser.html", error=error)


@app.route("/cuser", methods=["POST"])
def cuser():

    try:
        new_entry = models.User(request.form["username"], request.form["password"])
        db.session.add(new_entry)
        db.session.commit()
        flash("New user created successfully")
        db.session.commit()
        return redirect(url_for("login"))

    except IntegrityError:
        db.session.rollback()
        error = "This username already exists!"
        flash(error)
        return redirect(url_for("create_user", error=error))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in.")
            return jsonify({"status": 0, "message": "Please log in."}), 401
        return f(*args, **kwargs)

    return decorated_function


@app.route("/add_post", methods=["POST"])
def add_entry():
    """Adds new post to the database."""
    if not session.get("logged_in"):
        abort(401)
    new_entry = models.Post(request.form["title"], request.form["text"])
    db.session.add(new_entry)
    db.session.commit()
    flash("New entry was successfully posted")
    return redirect(url_for("index"))

@app.route("/add_comment", methods=["POST"])
def add_comment():
    """Adds new post to the database."""
    if not session.get("logged_in"):
        abort(401)
    new_comment = models.Comment(request.form["text"], request.form["post_id"], request.form["username"])
    db.session.add(new_comment)
    db.session.commit()
    flash("New entry was successfully posted")
    return redirect(url_for("post_page"))



# @app.route("/delete/<int:post_id>", methods=["GET"])
# @login_required
# def delete_entry(post_id):
#     """Deletes post from database."""
#     result = {"status": 0, "message": "Error"}
#     try:
#         new_id = post_id
#         db.session.query(models.Post).filter_by(id=new_id).delete()
#         db.session.commit()
#         result = {"status": 1, "message": "Post Deleted"}
#         flash("The entry was deleted.")
#     except Exception as e:
#         result = {"status": 0, "message": repr(e)}
#     return jsonify(result)



@app.route("/search/", methods=["GET"])
def search():
    query = request.args.get("query")
    entries = db.session.query(models.Post)
    if query:
        return render_template("search.html", entries=entries, query=query)
    return render_template("search.html")


if __name__ == "__main__":
    app.run()

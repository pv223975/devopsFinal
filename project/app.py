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
    send_from_directory
)
from flask_uploads import IMAGES, UploadSet, configure_uploads
from flask_sqlalchemy import SQLAlchemy

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

#image post stuff
photos = UploadSet("photos", IMAGES)
app.config["UPLOADED_PHOTOS_DEST"] = os.path.join(app.root_path, "static/images")
configure_uploads(app, photos)

from project import models

@app.route("/")
def index():
    """Searches the database for entries, then displays them."""
    entries = db.session.query(models.Post)
    return render_template("index.html", entries=entries)


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
    username = request.form["username"]
    # Check if the user with the provided username and password exists
    user = db.session.query(models.User).filter_by(uName=username).first()
    if user is not None:
        error = "Invalid username or password"
        """add new user to database"""
    else:
        new_entry = models.User(request.form["username"], request.form["password"])
        db.session.add(new_entry)
        db.session.commit()
        flash("New user created successfully")

    return redirect(url_for("login"))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in.")
            return jsonify({"status": 0, "message": "Please log in."}), 401
        return f(*args, **kwargs)

    return decorated_function


@app.route("/add", methods=["POST"])
def add_entry():
    """Adds new post to the database."""
    if not session.get("logged_in"):
        abort(401)
    new_entry = models.Post(request.form["title"], request.form["text"])
    db.session.add(new_entry)
    db.session.commit()
    flash("New entry was successfully posted")
    return redirect(url_for("index"))

@app.route("/viewimages", methods=["POST", "GET"])
def viewimages(): 
    files = os.listdir(os.path.join(app.static_folder, "images"))
    return render_template("viewimages.html", files=files)
    #still need to display these better and add user info, ability to delete
    #but they do display now
    #also figure out why gifs don't load
    #"file type not allowed" error too


@app.post("/add_image")
def upload_file():
    if request.method == "POST" and "photo" in request.files:
        photos.save(request.files["photo"])
        flash("Photo saved successfully.")
        return redirect(url_for("viewimages"))

@app.route("/delete/<int:post_id>", methods=["GET"])
@login_required
def delete_entry(post_id):
    """Deletes post from database."""
    result = {"status": 0, "message": "Error"}
    try:
        new_id = post_id
        db.session.query(models.Post).filter_by(id=new_id).delete()
        db.session.commit()
        result = {"status": 1, "message": "Post Deleted"}
        flash("The entry was deleted.")
    except Exception as e:
        result = {"status": 0, "message": repr(e)}
    return jsonify(result)


@app.route("/search/", methods=["GET"])
def search():
    query = request.args.get("query")
    entries = db.session.query(models.Post)
    if query:
        return render_template("search.html", entries=entries, query=query)
    return render_template("search.html")


if __name__ == "__main__":
    app.run()

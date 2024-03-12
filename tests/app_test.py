import json
from pathlib import Path

import pytest

from project.app import app, db
from project.models import User, Post

TEST_DB = "test.db"


@pytest.fixture
def client():
    BASE_DIR = Path(__file__).resolve().parent.parent
    app.config["TESTING"] = True
    app.config["DATABASE"] = BASE_DIR.joinpath(TEST_DB)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR.joinpath(TEST_DB)}"

    with app.app_context():
        db.create_all()  # setup

        # creates user for tests to reference
        new_entry = User(uName='testuser', pWord='password')
        db.session.add(new_entry)
        db.session.commit()

        yield app.test_client()  # tests run here
        db.session.remove()
        db.drop_all()  # teardown

def login(client, username, password):
    """Login helper function"""
    return client.post(
        "/login",
        data=dict(username=username, password=password),
        follow_redirects=True,
    )

def logout(client):
    """Logout helper function"""
    return client.get("/logout", follow_redirects=True)

def test_index(client):
    response = client.get("/", content_type="html/text")
    assert response.status_code == 200

def test_database(client):
    """initial test. ensure that the database exists"""
    tester = Path("test.db").is_file()
    assert tester

def test_db_status(client):
    # # ALTERED test_empty_db TO READ DB INSTEAD OF RELYING ON ALERTS
    # """Ensure database is blank"""
    # table_status = db.session.query(User).first()
    # assert table_status is not None
    """Test if DB was written on"""
    table_status = db.session.query(User).first()
    assert table_status is not None

def test_added_user(client):
    """Test if testuser was input to DB"""
    retrieved_user = db.session.query(User).filter_by(uName="testuser").first()
    assert retrieved_user is not None

def test_login_logout(client):
    """Test login and logout using helper functions"""
    rv = login(client, 'testuser', 'password')
    assert b"Logged in:" in rv.data
    rv = logout(client)
    assert b"You were logged out" in rv.data

def test_testuser_pass(client):
    """Test login succeeds with valid user and password"""
    rv = login(client, 'testuser', 'password')
    assert b"Logged in:" in rv.data
    rv = logout(client)

def test_testuser_wrongpass(client):
    """Test login fail with incorrect password"""
    rv = login(client, "testuser" , "wrongpassword")
    assert b"Invalid username or password" in rv.data
    rv = logout(client)

# test1 - error when navigating while loggedout
def test_access_without_login(client):
    """Test error when navigating without login"""
    rv = logout(client)
    response = client.post("/add")
    assert response.status_code == 401

def test_messages(client):
    """Ensure that user can post messages"""
    login(client, 'testuser', 'password')
    rv = client.post(
        "/add_post",
        data=dict(title="<Hello>", text="<strong>HTML</strong> allowed here"),
        follow_redirects=True,
    )
    assert b"New entry was successfully posted" in rv.data
    logout(client)

# DISABLED BY LUKE - NEED TO FIX
# def test_delete_message(client):
#     """Ensure the messages are being deleted"""
#     rv = client.get("/delete/1")
#     data = json.loads(rv.data)
#     assert data["status"] == 0
#     login(client, app.config["USERNAME"], app.config["PASSWORD"])
#     rv = client.get("/delete/1")
#     data = json.loads(rv.data)
#     assert data["status"] == 1

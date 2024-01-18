# Flaskr Social Media

Flaskr -- a mini-blog-like-app -- is the app that you build for the official Flask [tutorial](https://flask.palletsprojects.com/en/3.0.x/tutorial/).

## Install requirements

Be sure you have pip3 installed already (sudo apt install python3-pip)

pip3 install -r requirements.txt

python3 create_db.py # create the sqlite3 database

## Run Flaskr

python3 -m flask -A project/app.py run --host=0.0.0.0    # This runs on port 5000 by default, use --port=#### to specify another port

## Run Tests

python3 -m pytest

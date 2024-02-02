from project.app import db


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    text = db.Column(db.String, nullable=False)

    def __init__(self, title, text):
        self.title = title
        self.text = text

    def __repr__(self):
        return f"<title {self.title}>"

class User(db.Model):
    id = db.Column(Db.Integer, primary_key=True)
    uName = db.Column(db.String, nullable=False)
    pWord = db.Column(db.String, nullable=False)

    def __init__(self, uName, pWord):
        self.uName = uName
        self.pWord = pWord

    def __repr__(self):
        return f"<title {self.uName}>"
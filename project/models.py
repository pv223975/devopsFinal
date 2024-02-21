from project.app import db


friends = db.Table(
    'friends',
    db.Column('user_name', db.String, db.ForeignKey('user.uName'), primary_key=True),
    db.Column('friend_name', db.String, db.ForeignKey('user.uName'), primary_key=True)
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    text = db.Column(db.String, nullable=False)

    def __init__(self, title, text):
        self.title = title
        self.text = text

    def __repr__(self):
        return f"<title {self.title}>"
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    text = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)

    # Establish the relationship with the Post model
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))

    def __init__(self, text, post_id, username):
        self.text = text
        self.post_id = post_id
        self.username = username

    def __repr__(self):
        return f"<Comment {self.text}>"
   
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uName = db.Column(db.String, nullable=False, unique=True)
    pWord = db.Column(db.String, nullable=False)
    friends = db.relationship(
        'User',
        secondary=friends,
        primaryjoin=(friends.c.user_name == uName),
        secondaryjoin=(friends.c.friend_name == uName),
        lazy='dynamic'
    )

    def __init__(self, uName, pWord):
        self.uName = uName
        self.pWord = pWord

    def __repr__(self):
        return f"<User {self.uName}>"
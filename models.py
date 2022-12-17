from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """Users."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String(20), nullable=False,  unique=True)

    password = db.Column(db.Text, nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)
    
    first_name = db.Column(db.String(30), nullable=False)
    
    last_name = db.Column(db.String(30), nullable=False)

    city = db.Column(db.Text, nullable=False, default='Los Angeles')
    state = db.Column(db.Text, nullable=False, default='CA')

    @classmethod
    def register(cls, username, pwd, email, first_name, last_name, city, state):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8,  email=email, first_name=first_name, last_name=last_name, city=city, state=state)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False


class CollabBoard(db.Model):
    """Board."""

    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.Text, nullable=False)

    archive=db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    users = db.relationship('User', backref='boards')


class CollabList(db.Model):
    """List."""

    __tablename__ = 'colists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.Text, nullable=False)

    boards_id = db.Column(db.Integer, db.ForeignKey('boards.id'))

    boards = db.relationship('CollabBoard', backref='colists')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    users = db.relationship('User', backref='colists')

class CollabCard(db.Model):
    """Card."""

    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)

    lists_id = db.Column(db.Integer, db.ForeignKey('colists.id'))
    boards_id = db.Column(db.Integer, db.ForeignKey('boards.id'))
    colists = db.relationship('CollabList', backref='cards')
    boards = db.relationship('CollabBoard', backref='cards')


    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    users = db.relationship('User', backref='cards')


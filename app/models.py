from app import db, app
import flask_whooshalchemy as whooshalchemy

ROLE_USER = 0
ROLE_ADMIN = 1

import sys
if sys.version_info >= (3, 0):
    enable_search = False
else:
    enable_search = True
    import flask.ext.whooshalchemy as whooshalchemy

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(120), unique = True)
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.first_name)

class Post(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(5000))
    subject = db.Column(db.String(10))
    # Special characteristic - Bool
    attendance = db.Column(db.String(64))
    # Those who counts for rating
    teaching = db.Column(db.Integer)
    material = db.Column(db.Integer)
    participation = db.Column(db.Integer)
    # Do not count for rating
    difficulty = db.Column(db.Integer)
    # General rating
    rating = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)


class Professor(db.Model):
    __searchable__ = ['first_name', 'last_name']

    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    department = db.Column(db.String(64))
    # AVERAGE(teaching, material, participation)
    rating = db.Column(db.Float)
    posts = db.relationship('Post', backref = 'about', lazy = 'dynamic')
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'))

    def __repr__(self):
        return '<Professor %r>' % (self.first_name)
#whooshalchemy.whoosh_index(app, Professor)

if enable_search:
    whooshalchemy.whoosh_index(app, Professor)


class College(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    college_name = db.Column(db.String(64), unique = True)
    college_acronym = db.Column(db.String(8), unique = True)
    state = db.Column(db.String(2), unique = False)
    rating = db.Column(db.Float)
    professors = db.relationship('Professor', backref = 'college', lazy = 'dynamic')
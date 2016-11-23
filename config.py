#Keys for WTForms
WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True

SOCIAL_FACEBOOK = {
    'consumer_key': '730787893632867',
    'consumer_secret': '7f09822508f5abc3e9fe6a581de83ebe',
            'request_token_params': {
            'scope': 'email'
        }
}

WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50

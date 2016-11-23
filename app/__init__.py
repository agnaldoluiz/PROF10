from flask import Flask, redirect, url_for, session
from flask_oauth import OAuth
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
#load config archive \config.py
app.config.from_object('config')

#Set the DB
db = SQLAlchemy(app)
oauth = OAuth()

#Login

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key= '730787893632867',
    consumer_secret= '7f09822508f5abc3e9fe6a581de83ebe',
    request_token_params={'scope': 'email'}
)

from app import models, views

if os.environ.get('HEROKU') is not None:
    import logging
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('microblog startup')

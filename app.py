from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads

import MySQLdb

# SQL untuk Excel
database = MySQLdb.connect(
    user='root', password='root', host='localhost', database='toppgun', port=8889) #PORTNYA SESUAIKAN DENGAN DB

app = Flask(__name__)

####INI###########
files = UploadSet('files', ('pdf','pptx')) #bisa pakai (IMAGES + TEXT + ('py','pptx','docx')) #nama 'files' di dalam upload set samain aja karena ngaruh ke configure_uploads

####INI###########
app.config['SECRET_KEY'] = 'ghjdfdsfybskcvhskdjfhcsd7sdncudsaduey'
app.config['UPLOADED_FILES_DEST'] = 'toppgunfiles'
# app.config['UPLOADED_FILES_ALLOW'] = ['pdf', 'pptx']
# app.config['UPLOADED_FILES_DENY'] = ['.docx']

configure_uploads(app, files)


app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:root@localhost:8889/toppgun' #PORTNYA SESUAIKAN DENGAN DB

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

login_manager.login_view = 'login' #mengarahkan ke def login kalo masuk profile tanpa login

from views import *

if __name__ == '__main__':
    app.run(debug=True)

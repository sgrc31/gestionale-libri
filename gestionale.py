#!/usr/bin/env python3

import os
from flask import Flask, render_template
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname('.'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite///{}'.format(os.path.join(basedir, 'database.sqlite'))
db = SQLAlchemy(app)
manager = Manager(app)


#----------------------
#  Classi Database
#----------------------



#----------------
# Start app
#----------------
if __name__ == '__main__':
    manager.run()

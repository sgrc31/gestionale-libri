#!/usr/bin/env python3

import os
import csv
from flask import Flask, render_template
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc

basedir = os.path.abspath(os.path.dirname('.'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(os.path.join(basedir, 'database.sqlite'))
db = SQLAlchemy(app)
manager = Manager(app)


#----------------------------
# Tabelle Helpers Database
#----------------------------
adoptions = db.Table('adoptions',
                     db.Column('book_id', db.Integer, db.ForeignKey('books.id')),
                     db.Column('grade_id', db.Integer, db.ForeignKey('grades.id'))
                     )


#----------------------
#  Classi Database
#----------------------
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.Text, nullable = False)
    ean = db.Column(db.Text, nullable = False, unique = True)
    author = db.Column(db.Text, nullable = False)
    subject = db.Column(db.Text, nullable = False)
    publisher = db.Column(db.Text, nullable = False)
    adopted_by = db.relationship('Grade', secondary = adoptions, backref = db.backref('adopted_books', lazy = 'dynamic'))

    def __init__(self, title, ean, author = 'default', subject = 'default', publisher = 'default'):
        self.title = title
        self.ean = ean
        self.author = author
        self.subject = subject
        self.publisher = publisher

    @classmethod
    def from_file(cls, filename = 'data.csv'):
        with open(filename, newline = '') as csvfile:
            csvreader = csv.DictReader(csvfile, fieldnames = ('title', 'ean', 'author', 'subject', 'publisher'))
            for row in csvreader:
                try:
                    db.session.add(cls(row['title'], row['ean'], row['author'], row['subject'], row['publisher']))
                    db.session.commit()
                except exc.IntegrityError:
                    db.session.rollback()
                


class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text, nullable = False)

    def __init__(self, grade):
        self.name = classe

#------------
#  Routes
#------------
@app.route('/')
def index():
    return render_template('index.html',
                    books_list = Book.query.all()
                    )

#----------------
# Start app
#----------------
if __name__ == '__main__':
    manager.run()

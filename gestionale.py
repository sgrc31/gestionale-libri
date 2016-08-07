#!/usr/bin/env python3

import os
import csv
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from wtforms import StringField, BooleanField, SubmitField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import DataRequired
from sqlalchemy import exc

basedir = os.path.abspath(os.path.dirname('.'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(os.path.join(basedir, 'database.sqlite'))
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'you-will-never-guess'
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
        self.name = grade


#----------------
# Classi Forms
#----------------
class TestForm(Form):
    grades = QuerySelectField('Grades', get_label='name')

class LoginForm(Form):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class TestMulti(Form):
    da_comprare = QuerySelectMultipleField('da comprare', get_label='title')
    

#------------
#  Routes
#------------
@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        #session['messaggio'] = form.openid.data
        #flash('Inseriti: {} e {}'.format(form.openid.data, str(form.remember_me.data)))
        session['messaggio'] = form.openid.data
        return redirect(url_for('prova'))
    return render_template('index.html',
                           form = form
                           )
@app.route('/prova', methods=['GET', 'POST'])
def prova():
    #messaggio = session['messaggio']
    #nome = request.args.get('nome')
    return render_template('prova.html',
                           nome = session['messaggio']
                           )

@app.route('/test', methods=['GET', 'POST'])
def test():
    form = TestForm()
    #form.grades.choices = [(x.id, x.name) for x in Grade.query.all()]
    form.grades.query = Grade.query.all()
    if form.validate_on_submit():
        flash('{}'.format(form.grades.data.name))
        lista = Grade.query.filter_by(id=form.grades.data.id).first().adopted_books
        return render_template('test.html',
                               form = form,
                               lista_associata = lista
                               )
    return render_template('test.html',
                           form = form,
                           lista_associata = ''
                           )

@app.route('/test2', methods=['GET', 'POST'])
def test2():
    form = TestForm()
    form.grades.query = Grade.query.all()
    if form.validate_on_submit():
        form2 = TestMulti()
        form2.da_comprare.query = Grade.query.filter_by(id=form.grades.data.id).first().adopted_books
        nomome = form.grades.data.name
        #listona = Grade.query.filter_by(id=form.grades.data.id).first().adopted_books
        return render_template('secondo.html', nome_scuola = nomome, form = form2)
        #return redirect(url_for('secondo', nome_scuola = nomome, lista_libri_adottati = listona))
    return render_template('test2.html',
                           form = form
                           )

#@app.route('/secondo', methods=['GET', 'POST'])
#def secondo():
#    return render_template('secondo.html',
#                           nome_scuola = '',
#                           lista_libri_adottati = ''
#                           )

#@app.route('/terzo', methods=['GET', 'POST'])
#def terzo():
#    return render_template('terzo.html',
#                           nome_scuola = ''
#                           lista_libri_adottati = ''
#                           )
#----------------
# Start app
#----------------
if __name__ == '__main__':
    manager.run()

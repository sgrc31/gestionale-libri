#!/usr/bin/env python3

import os
import csv
from flask import Flask, render_template, request, flash, redirect, url_for, session
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

orders = db.Table('orders',
                  db.Column('book_id', db.Integer, db.ForeignKey('books.id')),
                  db.Column('student_id', db.Integer, db.ForeignKey('students.id'))
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
    ordered_by = db.relationship('Student', secondary = orders, backref = db.backref('ordered_books', lazy = 'dynamic'))

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

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text, nullable = False)
    phone = db.Column(db.Text, nullable = True)

    def __init__(self, name, phone=000000):
        self.name = name
        self.phone = phone


#----------------
# Classi Forms
#----------------
class TestForm(Form):
    grades = QuerySelectField('Grades', get_label='name')
    nome_ordine = StringField('Nome studente', validators=[DataRequired()])

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
    form = TestForm()
    form.grades.query = Grade.query.all()
    if form.validate_on_submit():
        session['nome_studente'] = form.nome_ordine.data
        session['id_scuola'] = form.grades.data.id
        session['nome_classe'] = form.grades.data.name
        return redirect(url_for('mezzopasso'))
    return render_template('index.html',
                           form = form,
                           lista_ordini = Student.query.all()
                           )


#@app.route('/mezzopasso', methods=['GET', 'POST'])
#def mezzopasso():
#    lista_libri_adottati = Grade.query.filter_by(id = session['id_scuola']).first().adopted_books
#    if request.method == "POST":
#        session['lista_libri_ordinati'] = request.form.getlist("test_check")
#        return redirect(url_for('terzopasso')) 
#    return render_template('mezzopasso.html',
#                           nome_studente = session['nome_studente'],
#                           nome_classe = session['nome_classe'],
#                           lista_libri_adottati = lista_libri_adottati
#                           )

@app.route('/mezzopasso', methods=['GET', 'POST'])
def mezzopasso():
    lista_libri_adottati = Grade.query.filter_by(id = session['id_scuola']).first().adopted_books
    if request.method == "POST":
        lista_libri_ordinati = request.form.getlist("test_check")
        studente = Student(session['nome_studente'])
        for id_libro in lista_libri_ordinati:
            studente.ordered_books.append(Book.query.filter_by(id=id_libro).first())
        db.session.commit()
        return redirect(url_for('index')) 
    return render_template('mezzopasso.html',
                           nome_studente = session['nome_studente'],
                           nome_classe = session['nome_classe'],
                           lista_libri_adottati = lista_libri_adottati
                           )

@app.route('/ordini/<ordine_id>/<ordine_nome>', methods=['GET', 'POST'])
def order_page(ordine_id, ordine_nome):
    return render_template('order_page.html',
                           ordine_id = ordine_id,
                           ordine_nome = ordine_nome,
                           lista_libri = Student.query.filter_by(id=ordine_id).first().ordered_books
                           )


@app.route('/terzopasso', methods=['GET', 'POST'])
def terzopasso():
    return render_template('terzopasso.html',
                           nome_studente = session['nome_studente'],
                           nome_classe = session['nome_classe'],
                           libri_ordinati = session['lista_libri_ordinati']
                           )
#----------------
# Start app
#----------------
if __name__ == '__main__':
    manager.run()

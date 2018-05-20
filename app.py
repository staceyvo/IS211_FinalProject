import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from wtforms import Form, validators, StringField, PasswordField, DateField, SelectField, TextAreaField

app = Flask(__name__)
app.secret_key = 'Mighty Ducks'


class LoginForm(Form):
    # create a login form
    username = StringField(u'Username', [validators.required(), validators.length(max=100)])
    password = PasswordField(u'Password', [validators.required(), validators.length(max=100)])

class NewEntryForm(Form):
    title = StringField(u'Title', [validators.required(), validators.length(max=200)])
    body = TextAreaField(u'Body', [validators.required(), validators.length(max=200000)])

@app.route('/', methods=['GET'])
def home_route():
    if 'username' in session:
        username = session['username']
        message = 'Logged in as ' + username

    else:
        message = "You are not logged in"

    return render_template('home_route.html', message=message)


@app.route('/login', methods=['POST', 'GET'])
def login():
    # entering the danger zone
    error = None

    if request.method == 'POST':
        if request.form['username'] != 'admin' or \
                        request.form['password'] != 'password':
            error = 'Invalid username or password. Please try again!'
        else:
            flash('You were successfully logged in')
            session['username'] = 'admin'
            return redirect(url_for('dashboard'))
    return render_template('login.html', my_form=LoginForm(), error=error)

@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    # TODO query for data when available
    if request.method == 'POST':
        con = sqlite3.connect('my_blog.db')
        cur = con.cursor()
        cur.execute('INSERT INTO post ("title", "text", "author", "published") VALUES (?,?,?,?)',
                    (request.form['title'], request.form['body'], session['username'], datetime.now()))
        con.commit()
        con.close()
    return render_template('dashboard.html', my_form=NewEntryForm())


@app.route('/create_database')
def create_database():
    if 'username' not in session:
        return redirect(url_for('login'))

    con = sqlite3.connect('my_blog.db')
    cur = con.cursor()
    with open('schema.sql') as fp:
        cur.executescript(fp.read())
    return redirect(url_for('dashboard'))



if __name__ == '__main__':
    app.run(host='localhost')

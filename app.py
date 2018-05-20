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

class EditEntryForm(Form):
    title = StringField(u'Title', [validators.length(max=200)])
    body = TextAreaField(u'Body', [validators.length(max=200000)])


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

    con = sqlite3.connect('my_blog.db')
    cur = con.cursor()
    if request.method == 'POST':
        cur.execute('INSERT INTO post ("title", "text", "author", "published") VALUES (?,?,?,?)',
                    (request.form['title'], request.form['body'], session['username'], datetime.now()))
        con.commit()

    posts = cur.execute('SELECT title, text, id FROM post').fetchall()
    con.close()
    return render_template('dashboard.html', my_form=NewEntryForm(), posts=posts)


@app.route('/delete/<id>')
def delete(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    con = sqlite3.connect('my_blog.db')
    con.cursor().execute('Delete FROM post WHERE id=?', id)
    con.commit()
    return redirect(url_for('dashboard'))


@app.route('/edit/<id>', methods=['POST', 'GET'])
def edit(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    con = sqlite3.connect('my_blog.db')
    cur = con.cursor()
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if title:
            cur.execute('UPDATE post SET title = ? WHERE id=?', (title, id))
        if body:
            cur.execute('UPDATE post SET text = ? WHERE id=?', (body, id))
        con.commit()

    post = con.cursor().execute('SELECT title, id, published, author, text FROM post WHERE id=?', id).fetchone()
    return render_template('edit.html', my_form=EditEntryForm(), post=post)


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

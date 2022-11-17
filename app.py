# import sqlite3
# from flask import Flask, render_template, request, url_for, flash, redirect
# from werkzeug.exceptions import abort
# from datetime import datetime
# from init_db import do_init

import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, url_for, flash, redirect
from config import config
import json


# def get_db_connection():
#     conn = sqlite3.connect('database.db')
#     conn.row_factory = sqlite3.Row
#     return conn



# def get_post(post_id):
#     conn = get_db_connection()
#     post = conn.execute('SELECT * FROM posts WHERE id = ?',
#                         (post_id,)).fetchone()
#     conn.close()
#     if post is None:
#         abort(404)
#     return post


def get_post(id):
    con = None
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor(cursor_factory=RealDictCursor)
        SQL = 'SELECT * FROM posts where id = %s;'
        cursor.execute(SQL, (id,))
        row = cursor.fetchone()
        cursor.close()
        return row
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()

def query_posts():
    con = None
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor()
        SQL = 'SELECT *FROM posts;'
        cursor.execute(SQL)
        row = cursor.fetchone()
        print(row)
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()

# print(query_posts())

app = Flask(__name__)
# do_init()
app.config['SECRET_KEY'] = 'do_not_touch_or_you_will_be_fired'


# this function is used to format date to a finnish time format from database format
# e.g. 2021-07-20 10:36:36 is formateed to 20.07.2021 klo 10:36
# def format_date(post_date):
#     isodate = post_date.replace(' ', 'T')
#     newdate = datetime.fromisoformat(isodate)
#     return newdate.strftime('%d.%m.%Y') + ' klo ' + newdate.strftime('%H:%M')


# this index() gets executed on the front page where all the posts are
@app.route('/')
def index():
    con = psycopg2.connect(**config())
    cursor = con.cursor()
    SQL = 'SELECT * FROM posts'
    cursor.execute(SQL) 
    columns = list(cursor.description)
    posts = cursor.fetchall()
    results = []
    for row in posts:
        row_dict = {}
        for i, col in enumerate(columns):
            row_dict[col.name] = row[i]
        results.append(row_dict)
    # print(results)
# display

#     cursor.close()
# # we need to iterate over all posts and format their date accordingl
#     # for post in dictrows:
#     #     # using our custom format_date(...)
#     #     post['created'] = post['created']
    return render_template('index.html', posts=results)


# here we get a single post and return it to the browser
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)



# here we create a new post
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            con = psycopg2.connect(**config())
            cursor = con.cursor(cursor_factory=RealDictCursor)
            SQL = 'INSERT INTO posts (title, content) VALUES (%s, %s);'
            cursor.execute(SQL, (title, content))
            con.commit()
            cursor.close()
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            con = psycopg2.connect(**config())
            cursor = con.cursor(cursor_factory=RealDictCursor)
            SQL = 'UPDATE posts SET title = %s, content = %s  WHERE id = %s;'
            cursor.execute(SQL, (title, content, id))
            con.commit()
            cursor.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)


# Here we delete a SINGLE post.
@app.route('/<int:id>/delete', methods=('POST', 'DELETE'))
def delete(id):
    post = get_post(id)
    con = psycopg2.connect(**config())
    cursor = con.cursor(cursor_factory=RealDictCursor)
    SQL = 'DELETE FROM posts where id = %s;'
    cursor.execute(SQL, (id,))
    con.commit()
    cursor.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))



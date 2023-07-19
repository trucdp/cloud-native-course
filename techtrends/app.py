import sqlite3
import logging
import sys
import datetime


# format='%(asctime)s %(message)s',

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`


now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID


def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Define the main route of the web application


@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)

    if post is None:
        notification = timestamp + " Non-existing article is accessed"
        app.logger.info(notification)
        return render_template('404.html'), 404
    else:
        notification = timestamp + ' Post "'+ post["title"] +'" is accessed'
        app.logger.info(notification)
        return render_template('post.html', post=post)

# Define the About Us page


@app.route('/about')
def about():
    notification = timestamp + ' "About Us" page is retrieved'
    app.logger.info(notification)
    return render_template('about.html')

# Define the Heathcheck function


@app.route('/healthz')
def healthcheck():
    check_connection = 200
    string_heath="OK - healthy"

    #check connection to DB
    try: 
        connection = sqlite3.connect('database.db')
    except sqlite3.Error:
        check_connection = 500
        string_heath="ERROR - unhealthy"

    #check "posts" table exit or not
    try:
        table_check = connection.execute('SELECT * FROM posts').fetchall()
    except sqlite3.Error:
        check_connection = 500
        string_heath="ERROR - unhealthy"

    response = app.response_class(
        response=json.dumps(string_heath),
        status=check_connection
    )
    return response

# Define the Metric Func


@app.route('/metrics')
def get_metrics():
    connection = get_db_connection()
    count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    number_connection = connection.execute(
        'SELECT COUNT(*) AS active_connections FROM sqlite_master').fetchone()[0]
    connection.close()
    response = app.response_class(
        response=json.dumps(
            {"db_connection_count": number_connection, "post_count": count}),
        status=200
    )
    return response

# Define the post creation functionality


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()
            notification = timestamp + ' New article "'+title +'" is created'
            app.logger.info(notification)
            return redirect(url_for('index'))

    return render_template('create.html')


# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', port='3111')
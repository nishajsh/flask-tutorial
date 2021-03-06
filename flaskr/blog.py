from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)




@bp.route('/')
def index():
    db = get_db()
    db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN "user" u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    )
    posts = db.fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/post/<post_id>', methods=('GET', 'POST'))
def open_post(post_id):
    db = get_db()
    if request.method == 'POST':
        body = request.form['body']
        db.execute(
            "INSERT INTO comment (author_id, post_id, body) "
            "VALUES (%s, %s, %s)", (g.user['id'], post_id, body)
        )
        return redirect(url_for('blog.open_post', post_id=post_id))
    db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN "user" u ON p.author_id = u.id'
        ' WHERE p.id = %s', (post_id, )
    )
    post = db.fetchone()
    db.execute(
        'SELECT c.id, body, created, author_id, username'
        ' FROM comment c JOIN "user" u ON c.author_id = u.id'
        ' WHERE c.post_id = %s', (post_id, )
    )
    comments = db.fetchall()
    return render_template('blog/open_post.html', post=post, comments=comments)



@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (%s, %s, %s)',
                (title, body, g.user['id'])
            )
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')




def get_post(id, check_author=True):
    db = get_db()
    db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN "user" u ON p.author_id = u.id'
        ' WHERE p.id = %s',
        (id,)
    )
    post = db.fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post



@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = %s, body = %s'
                ' WHERE id = %s',
                (title, body, id)
            )
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)




@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = %s', (id,))
    return redirect(url_for('blog.index'))






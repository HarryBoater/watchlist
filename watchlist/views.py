from flask import request, url_for, flash, render_template
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import redirect

from watchlist import app, db
from watchlist.models import User, Movie


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 如果当前用户未登录, 则返回首页
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        # 获取表单数据
        title = request.form.get("title")
        year = request.form.get("year")

        # 验证表单数据
        if not title or not year or len(year) > 4 or len(title) > 40:
            flash("Invalid Input")
            return redirect(url_for('index'))
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()

        flash("Item Added")
        return redirect(url_for('index'))

    movies = Movie.query.all()
    return render_template("index.html", movies=movies)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name and len(name) > 20:
            flash("Invalid Input")
            return redirect(url_for('settings'))

        current_user.name = name
        # 等价于
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash("Update Setting Success")
        return redirect(url_for('index'))

    return render_template('settings.html')


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form.get("title")
        year = request.form.get("year")

        if not title or not year or len(year) > 4 or len(title) > 40:
            flash("Invalid Input")
            return redirect(url_for('edit', movie_id=movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向回主页
    return render_template("edit.html", movie=movie)


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash("Item Delete")
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash("Invalid Input")
            return redirect(url_for('login'))

        user = User.query.first()
        if username == user.username and user.check_validate(password):
            login_user(user)
            flash("Login Success")
            return redirect(url_for('index'))
        flash("Invalid username or password")
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout")
    return redirect(url_for('index'))

from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
from models import db, User, College, Review

@app.route('/')
def home():
    colleges = College.query.all()
    return render_template('home.html', colleges=colleges)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email    = request.form['email']
        password = generate_password_hash(request.form['password'])
        user     = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']
        user     = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/college/<int:college_id>', methods=['GET', 'POST'])
def college_detail(college_id):
    college = College.query.get_or_404(college_id)
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('Please log in to submit a review.', 'warning')
            return redirect(url_for('login'))
        content = request.form['content']
        rating  = int(request.form['rating'])
        review  = Review(content=content, rating=rating,
                         user_id=current_user.id, college_id=college.id)
        db.session.add(review)
        db.session.commit()
        flash('Review submitted!', 'success')
        return redirect(url_for('college_detail', college_id=college.id))
    reviews = Review.query.filter_by(college_id=college.id).all()
    avg     = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else 0
    return render_template('college_detail.html', college=college,
                           reviews=reviews, avg=avg)

@app.route('/search')
def search():
    query    = request.args.get('q', '')
    colleges = College.query.filter(
        College.name.ilike(f'%{query}%') |
        College.city.ilike(f'%{query}%') |
        College.state.ilike(f'%{query}%')
    ).all()
    return render_template('search.html', colleges=colleges, query=query)

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    colleges = College.query.all()
    reviews  = Review.query.all()
    users    = User.query.all()
    return render_template('admin.html', colleges=colleges,
                           reviews=reviews, users=users)

@app.route('/admin/add_college', methods=['POST'])
@login_required
def add_college():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    name    = request.form['name']
    city    = request.form['city']
    state   = request.form['state']
    college = College(name=name, city=city, state=state)
    db.session.add(college)
    db.session.commit()
    flash('College added!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/delete_review/<int:review_id>')
@login_required
def delete_review(review_id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted.', 'success')
    return redirect(url_for('admin'))
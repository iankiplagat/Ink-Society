
from flask import Flask, render_template, url_for, flash, redirect, abort, request
from . import main
from ..models import User, Post, Comment
from flask_login import login_required, current_user
from .forms import PostForm,CommentForm
from .. import db, photos
from ..request import get_quotes

@main.route("/", methods = ['GET'])
def home():
    quote=get_quotes()
    print(quote)
    
    post = Post.query.order_by(Post.date.desc()).all()
    
    return render_template('home.html', title='Home', posts=post, quotes=quote)


@main.route("/about")
def about():
    return render_template('about.html', title='About')


@main.route('/user/<uname>')
def profile(uname):
    user = User.query.filter_by(username = uname).first()

    if user is None:
        abort(404)

    return render_template("profile/profile.html", user = user)


@main.route('/user/<uname>/update/pic',methods= ['POST'])
@login_required
def update_pic(uname):
    user = User.query.filter_by(username = uname).first()
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        path = f'photos/{filename}'
        user.profile_pic_path = path
        db.session.commit()
    return redirect(url_for('main.profile',uname=uname))

@main.route('/create_post',methods = ['GET','POST'])
@login_required
def create_post():
    title = 'create_post'
    form = PostForm()
    print(form.errors)
    
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        user_id = current_user._get_current_object().id
        
        new_post = Post(title = title,content=content,user_id = user_id)
        
        db.session.add(new_post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for("main.home"))
    
    return render_template('create_post.html', title = title, form = form)


@main.route('/comment/<int:post_id>', methods = ['POST','GET'])
@login_required
def comment(post_id):
    form = CommentForm()
    post = Post.query.get(post_id)
    all_comments = Comment.query.filter_by(post_id = post_id).all()
    
    if form.validate_on_submit():
        comment = form.comment.data 
        post_id = post_id
        user_id = current_user._get_current_object().id
        new_comment = Comment(comment = comment,user_id = user_id,post_id = post_id)
        new_comment.save_c()
        
        return redirect(url_for('.comment', post_id = post_id))
    
    return render_template('comment.html', form =form, post = post,all_comments=all_comments)


@main.route("/home<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(location)

    return render_template('home.html', title='Home', posts=post)

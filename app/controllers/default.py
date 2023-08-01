from app import app, db
from flask import render_template, redirect, url_for, request, flash, abort
from app.models.forms import (
    FormSignUp,
    FormSignIn,
    FormEditProfile,
    FormCreatePost,
)
from app.models.tables import User, Post
from flask_login import login_user, logout_user, current_user, login_required


@app.route("/home")
@app.route("/")
def home():
    posts = Post.query.order_by(Post.id.desc())
    return render_template("home.html", posts=posts)


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/users")
@login_required
def users():
    list_users = User.query.all()
    return render_template("users.html", list_users=list_users)


@app.route("/login", methods=["GET", "POST"])
def login():
    form_signup = FormSignUp()
    form_signin = FormSignIn()

    if form_signup.validate_on_submit() and "submit_signup" in request.form:
        user = User(
            username=form_signup.username.data,
            email=form_signup.email.data,
            password=form_signup.pwd.data,
        )
        db.session.add(user)
        db.session.commit()
        flash(
            f"Account created successfully, email: {form_signup.email.data}",
            "alert-success",
        )
        return redirect(url_for("home"))
    if form_signin.validate_on_submit() and "submit_signin" in request.form:
        user = User.query.filter_by(email=form_signin.email.data).first()
        if user and user.verify_password(form_signin.pwd.data):
            login_user(user, remember=form_signin.remember.data)
            flash(
                f"Login successful, email: {form_signin.email.data}",
                "alert-success",
            )
            param_next = request.args.get("next")
            if param_next:
                return redirect(param_next)
            else:
                return redirect(url_for("home"))
        else:
            flash("Login failed, incorrect email or password", "alert-danger")

    return render_template(
        "login.html", form_signup=form_signup, form_signin=form_signin
    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/profile")
@login_required
def profile():
    profile_pic = url_for(
        "static", filename="profile_pics/{}".format(current_user.profile_pic)
    )
    return render_template("profile.html", profile_pic=profile_pic)


def save_image(image):
    """
    Saves the image uploaded by the user
    1 - Create a code to change the name of the image, avoiding repeated names
    2 - Reduce image size
    :param image: name of the image to be saved
    """
    import secrets
    import os
    from PIL import Image

    code_image = secrets.token_hex(8)
    name_image, extension = os.path.splitext(image.filename)
    complete_image_name = name_image + code_image + extension
    complete_path = os.path.join(
        app.root_path, "static/profile_pics", complete_image_name
    )
    size_image = (400, 400)
    low_image = Image.open(image)
    low_image.thumbnail(size_image)
    low_image.save(complete_path)
    return complete_image_name


def update_interests(form):
    """
    Updates the user's list of interests.
    1 - Create a list
    2 - Scrolls through the fields of the existing form
    3 - Adds the fields marked as True "field.data" to the list
    :param form: it is a form with boolean fields to be traversed by the
     function
    """
    interests_list = []
    for field in form:
        if "interests_" in field.name:
            if field.data:
                interests_list.append(field.label.text)
    return ";".join(interests_list)


@app.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = FormEditProfile()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.username = form.username.data
        if form.profile_pic.data:
            name_image = save_image(form.profile_pic.data)
            current_user.profile_pic = name_image
        if update_interests(form) == "":
            current_user.interests = "No info"
        else:
            current_user.interests = update_interests(form)
        db.session.commit()
        flash("Profile updated successfully", "alert-success")
        return redirect(url_for("profile"))
    elif request.method == "GET":
        form.email.data = current_user.email
        form.username.data = current_user.username
    profile_pic = url_for(
        "static", filename="profile_pics/{}".format(current_user.profile_pic)
    )
    return render_template(
        "edit_profile.html", profile_pic=profile_pic, form=form
    )


@app.route("/post/create", methods=["GET", "POST"])
@login_required
def create_post():
    form = FormCreatePost()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            body=form.body.data,
            id_author=current_user.id,
        )
        db.session.add(post)
        db.session.commit()
        flash("Post created successfully", "alert-success")
        return redirect(url_for("home"))
    return render_template("create_post.html", form=form)


@app.route("/post/<post_id>", methods=["GET", "POST"])
@login_required
def post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.author:
        form = FormCreatePost()
    else:
        form = None
    return render_template("post.html", post=post, form=form)


@app.route("/post/<post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.author:
        form = FormCreatePost()
        if request.method == "GET":
            form.title.data = post.title
            form.body.data = post.body
        elif form.validate_on_submit():
            post.title = form.title.data
            post.body = form.body.data
            db.session.commit()
            flash("Post successfully updated", "alert-success")
            return redirect(url_for("post", post_id=post.id))
    else:
        form = None
        return redirect(url_for("home"))
    return render_template("edit_post.html", post=post, form=form)


@app.route("/post/<post_id>/delete", methods=["GET", "POST"])
def delete_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.author:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted successfully", "alert-danger")
        return redirect(url_for("home"))
    else:
        abort(403)
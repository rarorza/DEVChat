from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
)
from app.models.tables import User
from flask_login import current_user


class FormSignUp(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(3, 20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    pwd = PasswordField("Password", validators=[DataRequired(), Length(6, 128)])
    confirm_pwd = PasswordField(
        "Confirm password", validators=[DataRequired(), EqualTo("pwd")]
    )
    submit_signup = SubmitField("SignUp")

    def validate_email(self, email):
        """
        Checks if the email exists in the database
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already exists")

    def validate_username(self, username):
        """
        Checks if the user exists in the database
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already exists")


class FormSignIn(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    pwd = PasswordField("Password", validators=[DataRequired(), Length(6, 128)])
    remember = BooleanField("Remember data")
    submit_signin = SubmitField("SignIn")


class FormEditProfile(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(3, 20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    profile_pic = FileField(
        "Update profile pic", validators=[FileAllowed(["jpg", "jpeg", "png"])]
    )
    interests_python = BooleanField("Python")
    interests_csharp = BooleanField("C#")
    interests_cplusplus = BooleanField("C++")
    interests_c = BooleanField("C")
    interests_java = BooleanField("Java")
    interests_javascript = BooleanField("JavaScript")
    interests_ruby = BooleanField("Ruby")
    interests_golang = BooleanField("Golang")
    submit_edit_profile = SubmitField("Save")

    def validate_email(self, email):
        """
        Checks if the user has changed their email, then checks if the email
        already exists on the platform.
        """
        if current_user.email != email.data:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    "A user with that email already exists. Register another email."
                )

    def validate_username(self, username):
        """
        Checks if the user has changed username, then checks if the username
        already exists on the platform
        """
        if current_user.username != username.data:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    "A user with that username already exist. Try another username."
                )


class FormCreatePost(FlaskForm):
    title = StringField(
        "Post title", validators=[DataRequired(), Length(1, 140)]
    )
    body = TextAreaField("Write your post here", validators=[DataRequired()])
    submit_button = SubmitField("Create Post")

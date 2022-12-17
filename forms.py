from flask_wtf import FlaskForm
from wtforms import StringField, DateField, PasswordField, FloatField, BooleanField, SelectField,TextAreaField

from wtforms.validators import InputRequired, Length, Optional, URL


states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]




class UserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Length(max=120)])
    first_name = StringField("First_name", validators=[InputRequired(), Length(max=30)])
    last_name = StringField("Last_name", validators=[InputRequired(), Length(max=30)])
    city = StringField("city", validators=[InputRequired(), Length(max=30)])
    state = SelectField("state", choices=[(st, st) for st in states])

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])


class boardForm(FlaskForm):
    """Form for adding boards."""

    # Add the necessary code to use this form
    name = StringField("name", validators=[
                       InputRequired(message="Name can't be blank")])
 

class listForm(FlaskForm):
    """Form for adding lists."""

    # Add the necessary code to use this form
    name = StringField("name", validators=[
                       InputRequired(message="Name can't be blank")])


class cardForm(FlaskForm):
    """Form for adding cards."""

    # Add the necessary code to use this form
    name = StringField("name", validators=[
                       InputRequired(message="Name can't be blank")])
    description = StringField("description")
    deadline = DateField("deadline")
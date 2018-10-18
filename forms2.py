from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    #Validators are used to give conditions for the username , password etc.
    name = StringField("Name" , validators=  [DataRequired()])
    surname = StringField("Surname" , validators= [DataRequired()])
    username = StringField("Username" , validators = [DataRequired() , Length( min = 5 , max = 15)])
    email = StringField("Email" , validators= [DataRequired() , Email()])
    password = PasswordField("Password" , validators = [DataRequired() , Length(min = 5 , max = 15)])
    confirmPass = PasswordField("Confirm Password" , validators = [DataRequired() , EqualTo("password")])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email" , validators= [DataRequired() , Email()])
    password = PasswordField("Password" , validators = [DataRequired() , Length(min = 6 , max = 15)])
    remember = BooleanField("Remember my information")
    submit = SubmitField("Log In")


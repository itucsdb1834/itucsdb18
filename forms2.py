from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, IntegerField
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

class EventForm(FlaskForm):
    name = StringField("Name" , validators=  [DataRequired()])
    place = StringField("Place" , validators=  [DataRequired()])
    day = IntegerField("Day" , validators=  [DataRequired()])
    month = IntegerField("Month" , validators=  [DataRequired()]) #date field olarak degistir
    year = IntegerField("Year" , validators=  [DataRequired()])
    explanation = StringField("Explanation" , validators=  [DataRequired()])
    submit = SubmitField("Create")


class TravelForm(FlaskForm):
    name = StringField("Name" , validators=  [DataRequired()])
    country = StringField("Country" , validators=  [DataRequired()])
    city = StringField("City" , validators=  [DataRequired()])
    owner = StringField("Owner (input username)" , validators=  [DataRequired()])
    time_interval = StringField("Time Interval" , validators=  [DataRequired()]) #date field olarak degistir
    explanation = StringField("Explanation" , validators=  [DataRequired()])
    submit = SubmitField("Create")

class ProfileForm(FlaskForm):
    email = StringField("Email" , validators= [DataRequired() , Email()])
    name = StringField("Name", validators=[DataRequired()])
    surname = StringField("Surname", validators=[DataRequired()])
    gender = RadioField('Gender', choices=[('M', 'Male'), ('F', 'Female')])
    age = IntegerField("Age")
    country = StringField("Country")
    city = StringField("City")
    hobbies = StringField("Hobbies")
    description = StringField("Description")
    submit = SubmitField("Update")

class GroupForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    isprivate = RadioField('Do you want to approve new participants before they join group?', choices=[('Y', 'Private'), ('N', 'Public')] , validators = [DataRequired()])
    description = StringField("Description")
    give_permission = RadioField('Can other participants alter group information?', choices=[('Y', 'Yes'), ('N', 'No')] , validators = [DataRequired()])
    submit = SubmitField("Create Group")


class PasswordForm(FlaskForm):
    password = PasswordField("Password" , validators = [DataRequired() , Length(min = 5 , max = 15)])
    confirmPass = PasswordField("Confirm Password" , validators = [DataRequired() , EqualTo("password")])
    submit = SubmitField("Update Password")

class DeleteForm(FlaskForm):
    submit =SubmitField("Delete My Account")

class JoinEventForm(FlaskForm):
    submit = SubmitField("Join Event")

class LeaveEventForm(FlaskForm):
    submit = SubmitField("Leave Event")

class ChangeEventForm(FlaskForm):
    location = StringField("Location", validators=[DataRequired()])
    day = IntegerField("Day" , validators=  [DataRequired()])
    month = IntegerField("Month" , validators=  [DataRequired()])
    year = IntegerField("Year" , validators=  [DataRequired()])
    explanation = StringField("Explanation", validators=[DataRequired()])
    submit = SubmitField("Update Event")

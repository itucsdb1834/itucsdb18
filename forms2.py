from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, IntegerField, TextField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
import datetime
from datetime import date

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
    time = datetime.datetime.now()
    hour = time.hour
    minute = time.minute
    mytime = str(hour)+'.'+str(minute)
    name = StringField("Name" , validators=  [DataRequired()])
    place = StringField("Place" , validators=  [DataRequired()])
    date = StringField("Date of Event",  default = date.today(),validators=[DataRequired()] )
    time = StringField('Event Time', default = mytime ,validators=[DataRequired()] )
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
    max_number = IntegerField("Maximum Number of Participants" ,validators=[DataRequired()] )
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
    date = StringField("Date of Event",validators=[DataRequired()] )
    time = StringField('Event Time' ,validators=[DataRequired()] )
    explanation = StringField("Explanation", validators=[DataRequired()])
    submit = SubmitField("Update Event")

class DeleteGroupForm(FlaskForm):
    submit3 = SubmitField("Delete Group")

class UpdateGroupForm(FlaskForm):
    submit4 = SubmitField("Update Group")

class AddPeopleForm(FlaskForm):
    username = StringField("Input username for adding participant" )
    submit1 = SubmitField("Add People")

class AddEventForm(FlaskForm):
    submit2 = SubmitField("Add Group Event")

class ShowGroupEvents(FlaskForm):
    submit5 = SubmitField("View Group Events")

class RequestForm(FlaskForm):
    submit = SubmitField("Create Request")

class UpdateGroupInfoForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    isprivate = RadioField('Do you want to approve new participants before they join group?', choices=[('Y', 'Private'), ('N', 'Public')] , validators = [DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    give_permission = RadioField('Can other participants alter group information?', choices=[('Y', 'Yes'), ('N', 'No')] , validators = [DataRequired()])
    max_number = IntegerField("Maximum Number of Participants" ,validators=[DataRequired()])
    submit = SubmitField("Update Group")

class AddComment(FlaskForm):
    subject = StringField("Subject", validators=[DataRequired()])
    comment = TextField("Comment", validators=[DataRequired()])
    send_notification = BooleanField("Send Notification", default = False )
    submit = SubmitField("Post Comment")

class UpdateComment(FlaskForm):
    subject = StringField("Subject", validators=[DataRequired()])
    comment = TextField("Comment", validators=[DataRequired()])
    send_notification = BooleanField("Send Notification", default = False )
    submit = SubmitField("Update Comment")

class CreateRequestForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    min_people = IntegerField("Minimum Number of People Required to Turn it into an Event" , validators=  [DataRequired()])
    explanation = StringField("Explanation", validators=[DataRequired()])
    submit = SubmitField("Create Request")

class SearchEventForm(FlaskForm):
    event_input = StringField( validators=[DataRequired()])
    search_with = SelectField(choices=[('aim', 'AIM'), ('msn', 'MSN')])
    search_event = SubmitField("Search")

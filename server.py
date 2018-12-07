from flask import Flask, render_template, url_for, flash , redirect, request, abort,request, current_app, send_from_directory
from user import User
from event import Event, Events
from profile import Profile, MyProfile
from group import Group, Groups
from comment import Comment, Comments
from dbconn import Database
from forms2 import LoginForm, RegistrationForm, EventForm, TravelForm, ProfileForm, DeleteForm, PasswordForm ,GroupForm, JoinEventForm, LeaveEventForm, ChangeEventForm, DeleteGroupForm, UpdateGroupForm, AddPeopleForm ,AddEventForm, ShowGroupEvents,UpdateGroupInfoForm, AddComment, UpdateComment
from flask_login import LoginManager
from flask_login.utils import login_required, login_user, current_user, logout_user
from psycopg2 import IntegrityError
from dbconn import ConnectionPool
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = '0fe07ce1917042a7119c446dfa541a05'

Database.initialise()

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    with ConnectionPool() as cursor:
        cursor.execute('SELECT * FROM user_table WHERE userid = %s', (user_id,))
        user_data = cursor.fetchone()
        if user_data is not None:
            email = user_data[4]
            passwrd = user_data[5]
            name = user_data[2]
            surname = user_data[3]
            id = user_data[0]
            username = user_data[1]
            user = User(name, surname, username, email, passwrd, id)
            return user
        else:
            return


@app.route("/home" , methods = ['GET','POST'])
def home_page():
    posts = MyProfile(current_user.username)
    events = Events()
    events.select_top_ten()
    if current_user.id is None:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            event = request.form['event_id']
            return redirect(url_for('events', event = event))
        return render_template("home.html" , title = "Home" ,posts = posts, events = events.arr)

@app.route("/delete_event" , methods = ['POST'])
def delete_event():
    event = request.form['event_id_delete']
    current_user.remove_event(event)
    flash(f'Event is deleted!' , 'success')
    return redirect(url_for('owned_events'))

@app.route("/update_event" , methods = ['GET' , 'POST'])
def update_event():
    event = request.form['event_id_update']
    return redirect(url_for('change_event' , event = event))

@app.route("/change_event/<event>" , methods = ['GET' , 'POST'])
def change_event(event):
    form = ChangeEventForm()
    posts = MyProfile(current_user.username)
    updated_event = Event(None,None,None,None,None,None,None,None)
    updated_event.read_with_id(event)
    if request.method == 'POST':
        if form.validate_on_submit():
            updated_event.update_event(form.location.data,form.day.data, form.month.data, form.year.data, form.explanation.data);
            flash(f'Your event is updated successfully!', 'success')
        return redirect(url_for('owned_events'))
    return render_template("update_event.html", title="Update Event", form=form, posts = posts, event = updated_event)

@app.route("/createevent", methods = ['GET' , 'POST'])
def create_event():
    posts= MyProfile(current_user.username)
    form = EventForm()
    if current_user.get_id() is None:
        return render_template("login.html")
    else:
        if request.method == 'POST':
            event = Event(form.name.data , form.place.data , current_user.id, form.day.data, form.month.data, form.year.data , form.explanation.data , None)
            event.save_to_db()
            flash(f'Your event is created with name {form.name.data}!' , 'success')
            return render_template("home.html" , title = "Home" , form = form, posts=posts)
        return render_template("createevent.html" , title = "Create" , form = form, posts = posts)

@app.route("/creategroup", methods = ['GET' , 'POST'])
def create_group():
    posts= MyProfile(current_user.username)
    form = GroupForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            group = Group(form.name.data , form.isprivate.data , current_user.id, form.description.data, form.give_permission.data, None)
            group.save_to_db()
            flash(f'Your group is created with name {form.name.data}!' , 'success')
            return redirect(url_for('owned_groups'))
    return render_template("creategroup.html" , title = "Create" , form = form, posts = posts)

@app.route("/owned_groups" , methods = ['GET' , 'POST'])
def owned_groups():
    posts = MyProfile(current_user.username)
    groups = Groups()
    groups.owned_groups(current_user.id)
    if request.method == 'POST':
        group = request.form['group_id']
        print(group)
        return redirect(url_for('group_info', group = group))
    return render_template("owned_groups.html" , title = "Owned Groups" ,posts = posts, groups = groups.arr)

@app.route("/group/<group>" , methods = ['GET' , 'POST'])
def group_info(group):
    posts = MyProfile(current_user.username)
    mygroup = Group(None,None,None,None,None,group)
    mygroup.read_with_id()
    owned = False
    if current_user.id == mygroup.owner:
        owned = True
    permission = mygroup.give_permission
    deleteform = DeleteGroupForm()
    updateform = UpdateGroupForm()
    addpeople = AddPeopleForm()
    addevent = AddEventForm()
    showevents = ShowGroupEvents()

    if request.method == 'POST':
        if deleteform.submit3.data and deleteform.validate_on_submit():
            mygroup.delete_group()
            flash(f'Group {mygroup.name} is deleted!' , 'success')
            return redirect(url_for('owned_groups'))
        elif addpeople.submit1.data and addpeople.validate_on_submit():
            try:
                mygroup.add_participant(addpeople.username.data)
                flash(f'User {addpeople.username.data} is added to group' , 'success')
            except:
                flash('User already in group or there is no such user!')
            return redirect(url_for('group_info' , group = group))
        elif updateform.submit4.data and updateform.validate_on_submit():
            return redirect(url_for('update_group_info' , group = group))

    if owned:
        return render_template("group.html" , title= 'Group', posts = posts , group = mygroup, deleteform = deleteform , updateform = updateform,
        addpeople = addpeople, addevent = addevent, showevents = showevents, owned = True, permission = True)
    elif permission:
        return render_template("group.html" , title= 'Group', posts = posts , group = mygroup, updateform = updateform,
        addpeople = addpeople, addevent = addevent, showevents = showevents, owned = False , permission = True)
    else:
        return render_template("group.html" , title= 'Group', posts = posts , group = mygroup, showevents = showevents , owned = False, permission = False)

@app.route("/update_group_info/<group>", methods=['GET', 'POST'])
def update_group_info(group):
    form = UpdateGroupInfoForm()
    posts = MyProfile(current_user.username)
    mygroup = Group(None, None, None, None, None, group)
    mygroup.read_with_id()
    if request.method == 'POST':
        if form.validate_on_submit():
            mygroup.update_group(form.name.data,form.isprivate.data,form.description.data,form.give_permission.data)
            flash(f'Your group information is updated successfully!', 'success')
            return redirect(url_for('group_info', group = group))
    return render_template("update_group.html", title="Update Group", form=form, posts=posts, group=mygroup)

@app.route("/my_groups" , methods = ['GET' , 'POST'])
def my_groups():
    posts = MyProfile(current_user.username)
    groups = Groups()
    groups.my_groups(current_user.id)
    if request.method == 'POST':
        group = request.form['group_id']
        print(group)
        return redirect(url_for('group_info', group = group))
    return render_template("my_groups.html" , title = "My Groups" ,posts = posts, groups = groups.arr)


@app.route("/register" , methods = ['GET' , 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        my_user = User(form.name.data , form.surname.data, form.username.data , form.email.data , hashed_pass, None)
        my_user.save_to_db()
        flash(f'Your account is created with username {form.username.data}!' , 'success')
        return redirect(url_for("login"))
    return render_template("register.html" , title = "Register" , form = form)

@app.route("/" , methods = ['GET' , 'POST'])
@app.route("/login" , methods = ['GET' , 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if current_user.get_id() is not None:
            flash('You are already logged in !')
            return render_template("home.html" , title = "Login" , form = form)

        mail = form.email.data
        password = form.password.data
        new_user = User.get_with_email(mail)
        if new_user and bcrypt.check_password_hash(new_user.password , password):
            login_user(new_user)
            flash('Logged in successfuly!')
            posts = MyProfile(current_user.username)
            return redirect(url_for('home_page'))
        else:
            flash('Email or password incorrect')
            return render_template("login.html" , title = "Login" , form = form)
    else:
        if current_user.get_id() is not None:
            logout_user()
        return render_template('login.html', title= "Login" , form = form)



@app.route("/profile", methods=['GET'])
def profile_page():
    post = MyProfile(current_user.username)
    return render_template("profile.html" , title= 'Profile', posts = post)

@app.route("/profile/update", methods=['GET', 'POST'])
def update_profile():
    form = ProfileForm()
    posts = MyProfile(current_user.username)
    if request.method == 'POST':
        posts.update_my_profile(form.email.data,form.name.data, form.surname.data, form.gender.data, form.age.data, form.country.data, form.city.data, form.hobbies.data, form.description.data);
        flash(f'Your account is updated successfully!', 'success')
        return redirect(url_for('profile_page'))
    return render_template("update_profile.html", title="Update", form=form, posts = posts)


@app.route("/profile/delete" ,methods=['GET', 'POST'] )
def delete():
    form = DeleteForm()
    post = MyProfile(current_user.username)
    if request.method == 'POST':
        if form.validate_on_submit():
            # ilk once owner oldugu gruplar, eventler travellar var mi diye kontrol et random bir owner ata sonra sil
            current_user.delete_account()
            flash(f'Your account is deleted :(', 'success')
            return redirect(url_for('login'))
    return render_template("delete_account.html" , title= "Delete", posts = post, form = form)


@app.route("/event/<event>" , methods = ['POST', 'GET'])
def events(event):
    owned = current_user.check_owned(event)
    joined = current_user.check_participant_event(event)
    posts = MyProfile(current_user.username)
    commentform = AddComment()
    if joined:
        form = LeaveEventForm()
    else:
        form = JoinEventForm()
    if event is not None:
        myevent = Event(None,None,None,None,None,None,None,None)
        myevent.read_with_id(event)
        event_comments = Comments()
        event_comments.print_comments(event)
    if request.method == 'POST':
        if commentform.submit.data and commentform.validate_on_submit():
            newcomment = Comment(None, current_user.username, commentform.comment.data, commentform.subject.data, event, False, commentform.send_notification.data )
            newcomment.save_to_db()
        elif form.submit.data and form.validate_on_submit():
            if joined:
                myevent.delete_participant(current_user.id)
            else:
                myevent.add_participant(current_user.id)

        return redirect(url_for('events' , event = myevent.event_id))
    return render_template("event.html" , title= 'Event', posts = posts , event = myevent, form = form , owned = owned, comments = event_comments.comments, commentform = commentform)

@app.route('/update_comment' , methods = ['GET' , 'POST'])
def update_comment():
    commentid = request.form['comment_id_update']
    return redirect(url_for('change_comment' , commentid = commentid))

@app.route('/change_comment/<commentid>' , methods = ['GET' , 'POST'])
def change_comment(commentid):
    posts = MyProfile(current_user.username)
    form = UpdateComment()
    newcomment = Comment(commentid, None,None,None,None,None,None)
    event = newcomment.get_eventid()
    if request.method == 'POST':
        if form.validate_on_submit():
            newcomment.update_comment(form.comment.data, form.subject.data, form.send_notification.data)
            return redirect(url_for('events' , event = event))
    return render_template("update_comment.html" , title= 'Update Comment', posts = posts ,form = form )


@app.route('/delete_comment' , methods = ['POST'])
def delete_comment():
    if request.method == 'POST':
        commentid = request.form['comment_id_delete']
        newcomment = Comment(commentid, None, None, None, None, None, None )
        event = newcomment.get_eventid()
        newcomment.delete_comment()
        return redirect(url_for('events', event = event))

@app.route("/ownedevents" , methods = ['GET' , 'POST'])
def owned_events():
    events = Events()
    events.owned_events(current_user.id)
    posts = MyProfile(current_user.username)
    if request.method == 'POST':
        event = request.form['event_id']
        return redirect(url_for('events', event = event))
    return render_template("ownedevents.html" , title = "Owned Events" ,posts = posts, events = events.arr)

@app.route("/myevents" , methods = ['GET' , 'POST'])
def my_events():
    events = Events()
    events.my_events(current_user.id)
    posts = MyProfile(current_user.username)
    if request.method == 'POST':
        event = request.form['event_id']
        return redirect(url_for('events', event = event))
    return render_template("myevents.html" , title = "My Events" ,posts = posts, events = events.arr)




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

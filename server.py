from flask import Flask, render_template, url_for, flash , redirect, request, abort,request, current_app, send_from_directory
from user import User
from event import Event, Events
from profile import Profile, MyProfile
from group import Group, Groups
from comment import Comment, Comments
from dbconn import Database
from forms2 import LoginForm, RegistrationForm, EventForm, ProfileForm, DeleteForm, PasswordForm ,GroupForm
from forms2 import JoinEventForm, LeaveEventForm, ChangeEventForm, DeleteGroupForm, UpdateGroupForm, AddPeopleForm ,AddEventForm
from forms2 import ShowGroupEvents,UpdateGroupInfoForm, AddComment, UpdateComment, RequestForm, CreateRequestForm, SearchEventForm
from flask_login import LoginManager
from flask_login.utils import login_required, login_user, current_user, logout_user
from dbconn import ConnectionPool
from flask_bcrypt import Bcrypt
from request import Request, Requests
from news import New, News

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


@app.route("/home", methods=['GET','POST'])
@login_required
def home_page():
    posts = MyProfile(current_user.username)
    events = Events()
    events.select_top_ten()
    if request.method == 'POST':
        event = request.form['event_id']
        return redirect(url_for('events', event=event))
    return render_template("home.html", title="Home", posts=posts, events=events.arr)


@app.route("/SearchGroups" , methods = ['POST'])
@login_required
def search_group():
    if request.method == 'POST':
        filter_option = request.form['group_option']
        filter_input = request.form['input']
        if filter_input is None or filter_input == "":
            return redirect(url_for('my_groups'))
        return redirect(url_for('filtered_groups', option=filter_option,  input=filter_input ))


@app.route("/FilteredGroups/<option>/<input>", methods=['GET', 'POST'])
@login_required
def filtered_groups(option,input):
    posts = MyProfile(current_user.username)
    groups = Groups()
    try:
        groups.filtered_groups(option, input, current_user.get_id())
    except:
        flash('Try again.')
    if request.method == 'POST':
        group = request.form['group_id']
        return redirect(url_for('group_info', group=group))
    return render_template("my_groups.html", title="Found Groups", posts=posts, groups=groups.arr)


@app.route("/SearchEvents" , methods = ['POST','GET'])
@login_required
def search_events():
    filter_option = request.form['event_option']
    filter_input = request.form['input']
    if filter_input is None or filter_input =="":
        return redirect(url_for('home_page'))
    return redirect(url_for('filtered_events', option=filter_option,  input=filter_input ))


@app.route("/FilteredEvents/<option>/<input>", methods=['GET', 'POST'])
@login_required
def filtered_events(option,input):
    posts = MyProfile(current_user.username)
    events = Events()
    try:
        events.filtered_events(option, input)
    except:
        flash('Try again.')
    header = 'Found Events'
    if request.method == 'POST':
        event = request.form['event_id']
        return redirect(url_for('events', event=event))
    return render_template("myevents.html", title="Found Events", posts=posts, events=events.arr, header=header)


@app.route("/delete_event", methods=['POST'])
@login_required
def delete_event():
    event = request.form['event_id_delete']
    try:
        current_user.remove_event(event)
    except:
        flash('Could not remove event!')
        return redirect(url_for('owned_events'))
    flash(f'Event is deleted!' , 'success')
    return redirect(url_for('owned_events'))


@app.route("/delete_request" , methods = ['POST'])
@login_required
def delete_request():
    myrequest = request.form['request_id_delete']
    with ConnectionPool() as cursor:
        cursor.execute('SELECT group_id FROM request_table WHERE request_id = %s' ,(myrequest,))
        group = cursor.fetchone()[0]
    try:
        current_user.remove_request(myrequest)
    except:
        flash('Could not delete request!')
        return redirect(url_for('group_info', group = group))
    flash(f'Request is deleted!' , 'success')
    return redirect(url_for('group_info' , group = group))


@app.route("/upvote", methods=['POST'])
@login_required
def upvote_request():
    myrequest = request.form['request_id_upvote']
    with ConnectionPool() as cursor:
        cursor.execute('SELECT group_id FROM request_table WHERE request_id = %s' ,(myrequest,))
        group = cursor.fetchone()[0]
    try:
        if current_user.is_upvoted(myrequest):
            current_user.upvote(myrequest,-1 )
        else:
            current_user.upvote(myrequest,1)
    except:
        flash('Try again!')
        return redirect(url_for('group_info' , group = group))
    flash(f'Vote changed!' , 'success')
    return redirect(url_for('group_info' , group = group))


@app.route("/update_event" , methods = ['GET' , 'POST'])
@login_required
def update_event():
    event = request.form['event_id_update']
    return redirect(url_for('change_event' , event = event))


@app.route("/change_event/<event>" , methods = ['GET' , 'POST'])
@login_required
def change_event(event):
    form = ChangeEventForm()
    posts = MyProfile(current_user.username)
    updated_event = Event(None,None,None,None,None,None,None)
    updated_event.read_with_id(event)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                updated_event.update_event(form.location.data,form.date.data, form.time.data, form.explanation.data);
            except:
                flash('Could not update event!')
                return redirect(url_for('owned_events'))
            flash(f'Your event is updated successfully!', 'success')
            return redirect(url_for('owned_events'))
    return render_template("update_event.html", title="Update Event", form=form, posts = posts, event = updated_event)


@app.route("/createevent", methods = ['GET' , 'POST'])
@login_required
def create_event():
    posts= MyProfile(current_user.username)
    form = EventForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            event = Event(form.name.data , form.place.data , current_user.id, form.date.data, form.time.data , form.explanation.data , None)
            event.save_to_db()
            flash(f'Your event is created with name {form.name.data}!' , 'success')
            return redirect(url_for('owned_events'))
    return render_template("createevent.html" , title = "Create" , form = form, posts = posts)


@app.route("/creategroup", methods = ['GET' , 'POST'])
@login_required
def create_group():
    posts= MyProfile(current_user.username)
    form = GroupForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                group = Group(form.name.data , form.isprivate.data , current_user.id, form.description.data, form.give_permission.data, None, form.max_number.data)
                group.save_to_db()
            except:
                flash('Group could not be created!')
                return redirect(url_for('create_group'))
            flash(f'Your group is created with name {form.name.data}!' , 'success')
            return redirect(url_for('owned_groups'))
    return render_template("creategroup.html" , title = "Create" , form = form, posts = posts)


@app.route("/owned_groups" , methods = ['GET' , 'POST'])
@login_required
def owned_groups():
    posts = MyProfile(current_user.username)
    groups = Groups()
    groups.owned_groups(current_user.id)
    if request.method == 'POST':
        group = request.form['group_id']
        return redirect(url_for('group_info', group = group))
    return render_template("owned_groups.html" , title = "Owned Groups" ,posts = posts, groups = groups.arr)


@app.route("/group/<group>" , methods = ['GET' , 'POST'])
@login_required
def group_info(group):
    requests = Requests()
    requests.print_requests(group)
    posts = MyProfile(current_user.username)
    mygroup = Group(None,None,None,None,None,group,None)
    mygroup.read_with_id()
    owned = False
    joined = mygroup.check_participant(current_user.id)
    if current_user.id == mygroup.owner:
        owned = True
    permission = mygroup.give_permission
    deleteform = DeleteGroupForm()
    updateform = UpdateGroupForm()
    addpeople = AddPeopleForm()
    addevent = AddEventForm()
    showevents = ShowGroupEvents()
    create_request = RequestForm()

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
                flash('Please check max_number of croup or if the user already exists in the group!')
            return redirect(url_for('group_info' , group = group))
        elif updateform.submit4.data and updateform.validate_on_submit():
            return redirect(url_for('update_group_info' , group = group))
        elif create_request.submit.data and create_request.validate_on_submit():
            return redirect(url_for('create_request' , group = mygroup.group_id))
        elif addevent.submit2.data and addevent.validate_on_submit():
            return redirect(url_for('create_group_event', group = group))
        elif showevents.submit5.data and showevents.validate_on_submit():
            return redirect(url_for('group_events', group = group))

    if owned:
        return render_template("group.html" , title= 'Group', posts = posts , group = mygroup, deleteform = deleteform , updateform = updateform,
        addpeople = addpeople, addevent = addevent, showevents = showevents, owned = True, permission = True, create_request = create_request, requests = requests.arr , joined=joined)
    elif permission:
        return render_template("group.html" , title= 'Group', posts = posts , group = mygroup, updateform = updateform,
        addpeople = addpeople, addevent = addevent, showevents = showevents, owned = False , permission = True, create_request = create_request, requests = requests.arr , joined=joined)
    else:
        return render_template("group.html" , title= 'Group', posts = posts , group = mygroup, showevents = showevents , owned = False, permission = False, create_request = create_request, requests = requests.arr, joined=joined)


@app.route("/join_group", methods=['POST'])
@login_required
def join_group():
    groupid = request.form['group_id']
    mygroup = Group(None, None, None, None, None, groupid, None)
    mygroup.read_with_id()
    try:
        mygroup.add_participant(current_user.username)
        flash(f'You joined to group', 'success')
    except:
        flash('Please check max_number of group!')
    return redirect(url_for('group_info', group=groupid))


@app.route("/leave_group", methods=['POST'])
@login_required
def leave_group():
    groupid = request.form['group_id']
    mygroup = Group(None, None, None, None, None, groupid, None)
    mygroup.read_with_id()
    try:
        new = New(None, current_user.username, mygroup.owner_name, groupid, None, None, 'group', 'left', False,
                  None, None)
        new.save_to_db()
        with ConnectionPool() as cursor:
            cursor.execute('DELETE FROM group_user WHERE group_id = %s and user_id = %s', (groupid, current_user.id))
        flash(f'You leave the group', 'success')
        return redirect(url_for('my_groups'))
    except:
        flash('Please try again!')
        return redirect(url_for('group_info', group=groupid))


@app.route("/create_request/<group>", methods=['GET' , 'POST'])
@login_required
def create_request(group):
    posts = MyProfile(current_user.username)
    form = CreateRequestForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            myrequest = Request(None, form.name.data, current_user.username ,form.min_people.data, 0, form.explanation.data,group)
            myrequest.save_to_db()
            return redirect(url_for('group_info' , group = group))
    return render_template("create_request.html" , title= 'Create Request', posts = posts , form = form)


@app.route("/update_group_info/<group>", methods=['GET', 'POST'])
@login_required
def update_group_info(group):
    form = UpdateGroupInfoForm()
    posts = MyProfile(current_user.username)
    mygroup = Group(None, None, None, None, None, group,None)
    mygroup.read_with_id()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                mygroup.update_group(form.name.data,form.isprivate.data,form.description.data,form.give_permission.data,form.max_number.data)
            except:
                flash('Group information could not be updated!')
                return redirect(url_for('update_group_info', group = group))
            flash(f'Your group information is updated successfully!', 'success')
            return redirect(url_for('group_info', group = group))
    return render_template("update_group.html", title="Update Group", form=form, posts=posts, group=mygroup)

@app.route("/my_groups" , methods = ['GET' , 'POST'])
@login_required
def my_groups():
    posts = MyProfile(current_user.username)
    groups = Groups()
    groups.my_groups(current_user.id)
    if request.method == 'POST':
        group = request.form['group_id']
        return redirect(url_for('group_info', group = group))
    return render_template("my_groups.html" , title = "My Groups" ,posts = posts, groups = groups.arr)


@app.route("/register" , methods = ['GET' , 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        my_user = User(form.name.data , form.surname.data, form.username.data , form.email.data , hashed_pass, None)
        try:
            my_user.save_to_db()
        except:
            flash('An error occured!')
            return redirect(url_for("register"))
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
            flash(f'Logged in successfuly!' , 'success ')
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
@login_required
def profile_page():
    post = MyProfile(current_user.username)
    return render_template("profile.html" , title= 'Profile', posts = post)


@app.route("/profile/update", methods=['GET', 'POST'])
@login_required
def update_profile():
    form = ProfileForm()
    posts = MyProfile(current_user.username)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                posts.update_my_profile(form.email.data,form.name.data, form.surname.data, form.gender.data, form.age.data, form.country.data, form.city.data, form.hobbies.data, form.description.data);
            except:
                flash('Could not update profile!')
                return redirect(url_for('update_profile'))
        flash(f'Your account is updated successfully!', 'success')
        return redirect(url_for('profile_page'))
    return render_template("update_profile.html", title="Update", form=form, posts = posts)


@app.route("/profile/delete" ,methods=['GET', 'POST'])
@login_required
def delete():
    form = DeleteForm()
    post = MyProfile(current_user.username)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                current_user.delete_account()
            except:
                flash('Account could not be deleted! Please delete your groups and events first')
                return redirect(url_for('login'))
            flash(f'Your account is deleted :(', 'success')
            return redirect(url_for('login'))
    return render_template("delete_account.html" , title= "Delete", posts = post, form = form)


@app.route("/event/<event>" , methods = ['POST', 'GET'])
@login_required
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
        myevent = Event(None,None,None,None,None,None,None)
        myevent.read_with_id(event)
        event_comments = Comments()
        event_comments.print_comments(event)
    if request.method == 'POST':
        if commentform.submit.data and commentform.validate_on_submit():
            try:
                newcomment = Comment(None, current_user.username, commentform.comment.data, commentform.subject.data, event, False, commentform.send_notification.data)
                newcomment.save_to_db()
            except:
                flash("Could not comment!")
        elif form.submit.data and form.validate_on_submit():
            if joined:
                try:
                    myevent.delete_participant(current_user.id)
                except:
                    flash('An error occured!')
                    return redirect(url_for('events' , event = myevent.event_id))
            else:
                try:
                    myevent.add_participant(current_user.id)
                except:
                    flash('An error occured!')
                    return redirect(url_for('events' , event = myevent.event_id))
        return redirect(url_for('events' , event = myevent.event_id))
    return render_template("event.html" , title= 'Event', posts = posts , event = myevent, form = form , owned = owned, comments = event_comments.comments, commentform = commentform)


@app.route('/update_comment' , methods = ['GET' , 'POST'])
@login_required
def update_comment():
    commentid = request.form['comment_id_update']
    return redirect(url_for('change_comment' , commentid = commentid))


@app.route('/change_comment/<commentid>' , methods = ['GET' , 'POST'])
@login_required
def change_comment(commentid):
    posts = MyProfile(current_user.username)
    form = UpdateComment()
    newcomment = Comment(commentid, None,None,None,None,None,None)
    event = newcomment.get_eventid()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                newcomment.update_comment(form.comment.data, form.subject.data, form.send_notification.data)
            except:
                flash('Could not update comment!')
            return redirect(url_for('events' , event = event))
    return render_template("update_comment.html" , title= 'Update Comment', posts = posts ,form = form )


@app.route('/delete_comment' , methods = ['POST'])
@login_required
def delete_comment():
    if request.method == 'POST':
        commentid = request.form['comment_id_delete']
        newcomment = Comment(commentid, None, None, None, None, None, None )
        event = newcomment.get_eventid()
        try:
            newcomment.delete_comment()
        except:
            flash("Couldn't delete comment!")
        return redirect(url_for('events', event = event))


@app.route("/ownedevents" , methods = ['GET' , 'POST'])
@login_required
def owned_events():
    events = Events()
    events.owned_events(current_user.id)
    posts = MyProfile(current_user.username)
    if request.method == 'POST':
        event = request.form['event_id']
        return redirect(url_for('events', event = event))
    return render_template("ownedevents.html" , title = "Owned Events" ,posts = posts, events = events.arr)


@app.route("/myevents" , methods = ['GET' , 'POST'])
@login_required
def my_events():
    events = Events()
    events.my_events(current_user.id)
    header = 'My Events'
    posts = MyProfile(current_user.username)
    if request.method == 'POST':
        event = request.form['event_id']
        return redirect(url_for('events', event = event))
    return render_template("myevents.html" , title = "My Events" ,posts = posts, events = events.arr, header = header)


@app.route("/groupevents/<group>" , methods = ['GET' , 'POST'])
@login_required
def group_events(group):
    events = Events()
    events.group_events(current_user.id, group)
    posts = MyProfile(current_user.username)
    group_info=Group( None, None, None, None, None, group,None)
    group_info.read_with_id()
    header = group_info.name + ' events'
    if request.method == 'POST':
        event = request.form['event_id']
        return redirect(url_for('events', event=event))
    return render_template("myevents.html", title=group_info.name + " Events", posts=posts, events=events.arr, header = header)


@app.route("/creategroupevent/<group>", methods = ['GET' , 'POST'])
@login_required
def create_group_event(group):
    posts = MyProfile(current_user.username)
    form = EventForm()
    if request.method == 'POST':
        try:
            event = Event(form.name.data , form.place.data , current_user.id, form.date.data, form.time.data, form.explanation.data , group)
            event.save_to_db()
        except:
            flash('Could not create group event!')
            return redirect(url_for('create_group_event' , group = group))
        flash(f'Your event is created with name {form.name.data}!' , 'success')
        return redirect(url_for('group_events' , group = group))
    return render_template("createevent.html" , title = "Create" , form = form, posts = posts)


@app.route("/delete_participants", methods = ['POST'])
def delete_participants():
    if request.method == 'POST':
        participant = request.form['delete_participant']
        groupid = request.form['delete_participant_group']
        try:
            new = New(None, current_user.username, participant, groupid, None, None, 'group' , 'deleted you from', False, None,None )
            new.save_to_db()
            with ConnectionPool() as cursor:
                cursor.execute('SELECT userid FROM user_table where username = %s' , (participant,))
                userid = cursor.fetchone()[0]
                cursor.execute('DELETE FROM group_user WHERE group_id = %s and user_id = %s' ,(groupid, userid))
        except:
            flash('Could not delete participant!')
        return redirect(url_for('group_info' , group = groupid))

@app.route("/profiles", methods=['POST'])
def profile():
    profile = request.form['username']
    if profile == current_user.username:
        return redirect(url_for('profile_page'))
    post = Profile(profile)
    post.read_from_db()
    return render_template("profile.html" , title= 'Profile', posts = post)

@app.route("/news" , methods = ['GET' , 'POST'])
@login_required
def news():
    posts = MyProfile(current_user.username)
    news = News()
    news.print_news(current_user.username)
    if request.method == 'POST':
        id = request.form['news_id_delete']
        try:
            mynew = New(id, None, None, None, None, None, None , None, True,None)
            mynew.delete_new()
        except:
            flash('Could not delete new!')
        return redirect(url_for('news'))
    return render_template("news.html" , posts = posts, news = news.news_arr)

@app.route('/delete_news/<newsid>', methods = ['POST'])
@login_required
def delete_news(newsid):
    new = New(newsid, None, None, None, None, None, None, None, None ,None,None)
    new.delete_new()
    return redirect(url_for('news'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

from flask import Flask, render_template, url_for, flash, redirect
from forms import User
from forms2 import LoginForm, RegistrationForm
from dbconn import Database

app = Flask(__name__)

app.config['SECRET_KEY'] = '0fe07ce1917042a7119c446dfa541a05'

Database.initialise()

@app.route("/")
@app.route("/home")
def home_page():
    return render_template("home.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        my_user = User(form.name.data, form.surname.data, form.username.data, form.email.data, form.password.data, None)
        my_user.save_to_db()
        flash(f'Your account is created with username {form.username.data}!', 'success')
        return redirect(url_for('home_page'))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods = ['GET', "POST"])
def login():

    #form = LoginForm()
    #if form.validate_on_submit():
        #load_from_db_with_email()
    pass


@app.route("/events")
def events_page():
    return render_template("events.html", title='Events')


if __name__ == "__main__":
    app.debug=True
    app.run(host="0.0.0.0", port=8080, debug=True)

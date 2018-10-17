from flask import Flask, render_template, url_for, flash , redirect
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '0fe07ce1917042a7119c446dfa541a05'

posts = [
    {
        'author': 'Idil Ugurnal',
        'title': 'Big Italy Trip',
        'content': 'Visit Italy in 7 Days',
        'dates': '25 November 2018 - 2 December 2018'
    },
    {
        'author': 'Cagla Kaya',
        'title': 'Running Event in Besiktas',
        'content': 'Join us in running event designed by Nike.',
        'dates': '25 November 2018'
    }
]

@app.route("/")
@app.route("/home")
def home_page():
    return render_template("home.html" )

@app.route("/register" , methods = ['GET' , 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Your account is created with username {form.username.data}!' , 'success')
        return redirect(url_for('home_page'))
    return render_template("register.html" , title = "Register" , form = form)

@app.route("/login" , methods = ['GET' , "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'idilugurnal@gmail.com'and form.password.data == '1234567' :
            flash(f'You have logged in!' , 'success')
            return redirect(url_for('home_page'))
        else:
            flash('Login unsuccessful! Check username or password.' , 'danger')
    return render_template("login.html" , title = "Login" , form = form)

@app.route("/events")
def events_page():
    return render_template("events.html" , posts = posts, title= 'Events')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

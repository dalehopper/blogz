from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:123456@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'bobItsAboy!'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(6000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', "view_edit"]
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', title = "Our Blogz Users:", users = users)

@app.route('/blog', methods=['POST', 'GET'])
def view_edit():
    #handles new blog posting
    
    if request.method == 'POST':
        owner = User.query.filter_by(username=session['username']).first()
        error = ""
        blog_title = request.form['title']
        blog_body = request.form['body']
        if not (blog_title and blog_body):
            error = "The title and blog may not be blank!"
            return render_template("newpost.html", title = "Make a New Blog", error = error, blog_title = blog_title, blog_body = blog_body)
        new_blog = Blog(blog_title, blog_body, owner)
        db.session.add(new_blog)
        db.session.commit()
        return render_template('viewpost.html', title = new_blog.title, blog = new_blog)
    #handles both / redirect and link to main page
    blog_id = request.args.get("id")    
    user_id = request.args.get('user')
    users = User.query.all()
    if blog_id == None:
        if user_id ==None:
            blogs = Blog.query.all()
        else:
            blogs = Blog.query.filter_by(owner_id = user_id).all()
        return render_template('bloglist.html', title = 'Blogz!', blogs = blogs, users = users)
    #handles clicks on blog title links
    else:
        requested_blog = Blog.query.get(blog_id)
        return render_template('viewpost.html', title = requested_blog.title, blog = requested_blog)
@app.route('/newpost')
def add_blog():
    return render_template("newpost.html", title = "Make a New Blog")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html', title = "Log into Blogz")

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        

        # validate user's data
        errors = 0
        existing_user = User.query.filter_by(username=username).first()
        if not (username and password and verify):
            flash ('One or more fields is invalid!', 'error')
            errors +=1
        if existing_user:
            flash ('Sorry! That username is taken.  :(', 'error')
            errors +=1
        if password != verify:
            flash ('Passwords do not match!', 'error')
            errors +=1
        if (len(username) < 3 or len(password) < 3):
            flash ('Username and password must be at least 3 characters long!', 'error')
            errors +=1
        if errors >0:
            return redirect ('/signup')

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')


    return render_template('signup.html', title = "Sign up for Blogz!")

@app.route('/logout')
def logout():

    session.pop('username', None)
    return redirect('/blog')



if __name__ == '__main__':
    app.run()
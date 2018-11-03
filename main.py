from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:123456@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(6000))

    def __init__(self, title, body):
        self.title = title
        self.body = body
@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def view_edit():
    #handles new blog posting
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_blog = Blog(blog_title, blog_body)
        db.session.add(new_blog)
        db.session.commit()
        return render_template('viewpost.html', title = new_blog.title, blog = new_blog)
    #handles both / redirect and link to main page
    requested_id = request.args.get("id")    
    if requested_id == None:
        blogs = Blog.query.all()
        return render_template('index.html', title = 'Build A Blog!', blogs = blogs)
    #handles clicks on blog title links
    else:
        requested_blog = Blog.query.get(requested_id)
        return render_template('viewpost.html', title = requested_blog.title, blog = requested_blog)
@app.route('/add')
def add_blog():
    return render_template("newpost.html", title = "Make a New Blog")

if __name__ == '__main__':
    app.run()
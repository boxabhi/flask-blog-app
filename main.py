from flask import Flask, render_template, redirect,request,flash,url_for,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
from werkzeug.utils import secure_filename
import os
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/blogapp'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogapp'

db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'blogapp'  
login_manager = LoginManager()  
login_manager.init_app(app)

UPLOAD_FOLDER = r'C:\\Users\\user\\Documents\\Python\\flask\\newblog\\static\\image'
UPLOAD_PROFILE_FOLDER = r'C:\\Users\\user\\Documents\\Python\\flask\\newblog\\static\\image\\profile'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_PROFILE_FOLDER'] = UPLOAD_PROFILE_FOLDER

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_image = db.Column(db.String(300) , default= 'default.jpeg')
    password = db.Column(db.String(120), nullable=True)


class Posts(db.Model):
    user = db.Column(db.Integer , nullable=False)
    post_id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.String(5000), nullable=False)
    img = db.Column(db.String(200))
    created_at = db.Column(db.String(100))


@login_manager.user_loader
def load_user(user_id):
    return Users.get(id)

@app.route('/')
def hello():
    
    posts = Posts.query.order_by(Posts.post_id.desc()).all()
    users = Users.query.all()
    return render_template('index.html', posts = posts)

@app.route('/blog')
def blogPage():
    return render_template('blog.html')

@app.route('/detail-post/<id>')
def detail_post(id):
    post = Posts.query.filter_by(post_id = id).first()
    user = Users.query.filter_by(username = post.author).first()
    print('this is a post' , post)
    return render_template('post.html' , post = post , user = user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session:
        return redirect('dashboard')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        isEmailValid = Users.query.filter_by(email = email).first()
        
        if(isEmailValid):
             if isEmailValid.password == password:
                flash('Welcome')
                session['user'] = isEmailValid.username
                return render_template('dashboard/dashboard.html' , name = session)
           
        else:
             flash('Email doesn\'t exists')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email= request.form.get('email')
        username= request.form.get('username')
        password= request.form.get('password')
        checkIfHas = Users.query.filter_by(email = email).first()
        if checkIfHas:
            flash('User Already Exists', 'danger')
            session.clear()
            redirect('/register')
        else:
            entry = Users(email = email, username = username  , password= password)
            db.session.add(entry)
            db.session.commit()
            session.clear()
            flash('Account Created', 'danger')
            
            return redirect('/login')
    return render_template('register.html')


@app.route('/dashboard')

def dashboard():
    return render_template('dashboard/dashboard.html', name=session)


@app.route('/profile' , methods=['GET' , 'POST'])
def profile():
    session_user = session['user']
    user = Users.query.filter_by(username = session_user).first()

    if request.method == "POST":
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_PROFILE_FOLDER'], filename))

        user.profile_image = filename
        db.session.commit()
        flash('Profile Updated')
        return redirect('profile')

    return render_template('dashboard/profile.html' ,user = user,  name=session)

@app.route('/view')
def view():
    user = session['user']
    allData = Posts.query.filter_by(author = user).all()
    return render_template('dashboard/view.html' , name=session, allData = allData , session = session['user'])


@app.route('/addpost', methods = ['GET', 'POST'])
def addpost():
    if request.method == "POST":
        author = request.form.get('author')
        title = request.form.get('title')
        content = request.form.get('content')
        file = request.files['file']
        user =  session['user']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        addToDb = Posts(user = user,author = user , title = title, content = content ,img = filename)
        db.session.add(addToDb)
        db.session.commit()
        flash('Post Added Successfully!')
        return redirect('addpost')
          
    return render_template('dashboard/newpost.html', name=session)


@app.route('/edit/<id>', methods=['GET' , 'POST'])
def edit(id):
    post = Posts.query.filter_by(post_id = id).first()
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        file = request.files['file']
        user =  session['user']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        post.title = title
        post.content = content
        if file:
            post.img = filename
        db.session.commit()
        flash('Post Updated Successfully!')
    return render_template('dashboard/edit.html' , post = post , name = session)

@app.route('/detail-view/<user>-<slug>',methods=["GET" , 'POST'])
def detail_view(user ,slug):
    post = Posts.query.filter_by(title= slug , author = user).first()
    print(post)
    return render_template('dashboard/detail.html' , post = post ,name=session)

@app.route('/delete_post/<id>', methods=['GET','POST'])
def delete_post(id):
    post = Posts.query.filter_by(post_id = id).first_or_404()
    db.session.delete(post)
    db.session.commit()
    return redirect('/view')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('login')


@app.route('/admin')

def admin():
    return render_template('admin.html')



if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, Response, render_template,session, redirect,flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import uuid
import os

from db import db_init, db
from model import Files,User

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'
# SQLAlchemy config. Read more: https://flask-sqlalchemy.palletsprojects.com/en/2.x/
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)
app.config['CLIENT_ID'] = os.getenv("CLIENT_ID")
app.config['CLIENT_SECRET'] = os.getenv("CLIENT_SECRET")
app.config['REDIRECT_URI'] = 'http://127.0.0.1:5000/user/callback'

from discord import Oauth

def logged_in(f):
    @wraps(f)
    def logged_in_check(*args, **kwargs):
        try:
            if not session['key']:
                return redirect('/login')
        except:
            return redirect('/login')
        return f(*args, **kwargs)
    return logged_in_check


@app.route('/')
@logged_in
def index():
    return render_template("index.html")

@app.route('/files/<file>.<mimetype>')
def view(file,mimetype):
    img = Files.query.filter_by(name=f'{file}.{mimetype}').first()

    if not img:
        return 'Img Not Found!', 404

    return Response(img.img, mimetype=img.mimetype)

@app.route('/files/')
@logged_in
def files():
    files1 = Files.query.filter_by(user=session['key'])
    return render_template("files.html", files=files1)

@app.route('/manage/')
@logged_in
def view_pages():
    files1 = Files.query.filter_by(user=session['key'])
    return render_template("manage.html", files=files1)

@app.route('/settings/')
@logged_in
def settings():
    user = User.query.filter_by(key=session['key']).first()
    print('rr')
    return render_template("settings.html", user=user)

@app.route('/signup/')
def signup():
    return render_template("signup.html")

@app.route('/login/')
def login():
    return render_template("login.html")

@app.route('/login/discord/')
def discord_login():
    return redirect(Oauth.discord_login_url)

@app.route('/logout/')
def logout():
    session.pop('key', None)
    return redirect("/")

@app.route('/upload', methods=['POST'])
def upload():
    pic = request.files['pic']
    if not pic:
        return 'No pic uploaded!', 400

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        return 'Bad upload!', 400
    img = Files(img=pic.read(),user=session['key'], name=filename, mimetype=mimetype)
    db.session.add(img)
    db.session.commit()

    return redirect('/files/')

@app.route('/files/manage/id=<num>', methods=['POST'])
def files_manage(num):
    user = User.query.filter_by(key=session['key']).first()
    if user:
        if 'delete' in request.form:
            files1 = Files.query.filter_by(id=num).delete()
            db.session.commit()
            return redirect('/manage/')
        if 'rename' in request.form:
            files1 = Files.query.filter_by(id=num).first()
            rename = request.form["rename-name"]
            if rename in ('',' '):
                flash('Please rename the file correctly.')
                return redirect('/manage/')
            files1.name= f'{rename}.{files1.name[-3:]}'
            db.session.commit()
            return redirect('/manage/')
    return 'test', 400

@app.route('/user/create/', methods=['POST'])
def createuser():
    result = request.form.to_dict()
    if result['code'] == os.getenv("ADMIN_ACC_CODE"):
        password = generate_password_hash(result['password'], method='sha256')
        user = User(username=result['username'],password=password, external_id=None, admin=True, key=str(uuid.uuid1()), invite=None)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    else:
        code = User.query.filter_by(invite=result['code']).first()
    if not code:
        return 'no code', 401
    code.invite = str(uuid.uuid1().hex)[:6]
    password = generate_password_hash(result['password'], method='sha256')
    user = User(username=result['username'],password=password, external_id=None, admin=False, key=str(uuid.uuid1()), invite=None)
    db.session.add(user)
    db.session.commit()

    return redirect('/login')

@app.route('/user/authorize/', methods=['POST'])
def authorize():
    result = request.form.to_dict()
    session.pop('key', None)
    user = User.query.filter_by(username=result['username']).first()
    if user:
        if check_password_hash(user.password, result['password']):
            session['key'] = user.key
            return redirect('/')
        else:
            flash('Password is incorrect.')
            return redirect('/login')
    else:
        flash('Username is incorrect.')
        return redirect('/login')

@app.route('/user/callback/')
def callback():
    code = request.args.get("code")
    user_json = Oauth.discord_authenticate(code)
    user = User.query.filter_by(external_id=user_json.get('id')).first()
    if not user:
        flash('Discord login failed.')
        return redirect('/login')
    session['key'] = user.key
    return redirect('/')

@app.route('/user/invite/', methods=['POST'])
def create_invite():
    user = User.query.filter_by(key=session['key']).first()
    if user:
        if user.admin == True:
            user.invite = str(uuid.uuid1().hex)[:6]
            db.session.commit()
            return redirect('/settings')
        else:
            flash('Sorry, you need admin for that.')
            return redirect('/settings')

@app.route('/user/connections/', methods=['POST'])
def connect_discord():
    user = User.query.filter_by(key=session['key']).first()
    if user:
        user.external_id = str(request.form['discord_id'])
        db.session.commit()
        return redirect('/settings')
    else:
        flash('Something went wrong.')
        return redirect('/settings')

@app.route('/user/reset/', methods=['POST'])
def password_reset():
    user = User.query.filter_by(key=session['key']).first()
    if user:
        user.password = str(generate_password_hash(request.form['password'], method='sha256'))
        db.session.commit()
        session.pop('key', None)
        return redirect('/')

    return 405


if __name__ == "__main__":
    app.run(debug=True)

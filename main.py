from flask import Flask, request, Response, render_template
from werkzeug.utils import secure_filename

from db import db_init, db
from model import Files


app = Flask(__name__)
# SQLAlchemy conficg. Read more: https://flask-sqlalchemy.palletsprojects.com/en/2.x/
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/upload', methods=['POST'])
def upload():
    pic = request.files['pic']
    if not pic:
        return 'No pic uploaded!', 400

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        return 'Bad upload!', 400
    img = Files(img=pic.read(), name=filename, mimetype=mimetype)
    db.session.add(img)
    db.session.commit()

    return 'File Uploaded!', 200

@app.route('/<id>')
def ddimg(id):
    if id.isnumeric():
      img = Files.query.filter_by(id=id).first()
    else:
      img = Files.query.filter_by(name=id).first()
   
    if not img:
        return 'Img Not Found!', 404

    return Response(img.img, mimetype=img.mimetype)
   



@app.route('/tt')
def t():
  t = Files.query.all()
  return render_template("files.html", t=t)

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0", port=8080)
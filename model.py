from db import db


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Text, nullable=False)
    img = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, unique=True, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    external_id = db.Column(db.Text, unique=True, nullable=True)
    admin = db.Column(db.Boolean)
    key = db.Column(db.Text, unique=True, nullable=False)
    invite = db.Column(db.Integer, nullable=True, unique=True)

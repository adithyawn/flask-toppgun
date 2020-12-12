from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

################ DATABASE USER #####################

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    username = db.Column(db.String(30))
    password = db.Column(db.String(150))
    divisi = db.Column(db.String(30))
    kategori_wbs = db.Column(db.String(300))
    wbs_spesifik = db.Column(db.String(300))
    status = db.Column(db.Integer)
    join_date = db.Column(db.DateTime)

    posts = db.relationship('Post', backref='user', lazy='dynamic')

############### REFERENCE DATA #####################

#### WBS REFERENCE

class KategoriWbs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_kategori_wbs = db.Column(db.String(50), unique=True, nullable=False)
    kategori_wbs = db.Column(db.String(50))

    link_kategori_wbs = db.relationship(
        'InputWbs', backref='kategori_wbs', lazy='dynamic')


class WbsSpesifik(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_wbs_spesifik = db.Column(db.String(50), unique=True, nullable=False)
    wbs_spesifik = db.Column(db.String(50))
    id_kategori_wbs = db.Column(db.String(50))

    link_wbs_spesifik = db.relationship(
        'InputWbs', backref='wbs_spesifik', lazy='dynamic')


class WbsLevel2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_wbs_level2 = db.Column(db.String(50), unique=True, nullable=False)
    wbs_level2 = db.Column(db.String(50))
    id_wbs_spesifik = db.Column(db.String(50))

    link_wbs_level2 = db.relationship(
        'InputWbs', backref='wbs_level2', lazy='dynamic')


class WbsLevel3(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_wbs_level3 = db.Column(db.Integer, unique=True, nullable=False)
    wbs_level3 = db.Column(db.String(50))
    id_wbs_level2 = db.Column(db.String(50))

    # Penulisan WbsLevel3 di backref jadi wbs_level3
    link_wbs_level3 = db.relationship(
        'InputWbs', backref='wbs_level3', lazy='dynamic')


class InputWbs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    input_id_kategori_wbs = db.Column(
        db.String(300), db.ForeignKey('kategori_wbs.id_kategori_wbs'))
    input_id_wbs_spesifik = db.Column(
        db.String(300), db.ForeignKey('wbs_spesifik.id_wbs_spesifik'))
    input_id_wbs_level2 = db.Column(
        db.String(300), db.ForeignKey('wbs_level2.id_wbs_level2'))

    # Penulisan WbsLevel3 di backref jadi wbs_level3, disini terkait pada penulisan ForeignKey
    input_id_wbs_level3 = db.Column(
        db.String(300), db.ForeignKey('wbs_level3.id_wbs_level3'))


#### JENIS TOPP GUN REFERENCE

class JenisToppgun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_jenis_toppgun = db.Column(db.Integer, unique=True, nullable=False)
    data_jenis_toppgun = db.Column(db.String(300))

#### KATEGORI LEAN REFERENCE

class KategoriLean(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_kategori_lean = db.Column(db.Integer, unique=True, nullable=False)
    data_kategori_lean = db.Column(db.String(300))

#### DIVISI REFERENCE

class Divisi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_divisi = db.Column(db.Integer, unique=True, nullable=False)
    data_divisi = db.Column(db.String(50))

################ REKAP POST #####################

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_kategori_wbs = db.Column(db.String(300))
    post_wbs_spesifik = db.Column(db.String(300))
    post_wbs_level2 = db.Column(db.String(300))
    post_wbs_level3 = db.Column(db.String(300))
    post_judul = db.Column(db.String(300))
    post_deskripsi = db.Column(db.Text)
    post_jenis_toppgun = db.Column(db.String(300))
    post_kategori_lean = db.Column(db.String(300))
    post_file_url = db.Column(db.String(300))
    post_wbs_terkait = db.Column(db.Text)
    post_date = db.Column(db.DateTime)
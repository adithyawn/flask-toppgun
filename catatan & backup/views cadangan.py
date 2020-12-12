from flask import Flask, render_template, redirect, url_for, json, jsonify, request

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, FileField, PasswordField, SelectField, SubmitField, BooleanField
from wtforms.validators import InputRequired, length, DataRequired

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user


import xlrd
import MySQLdb

# from flask_login import login_user, login_required, current_user, logout_user, LoginManager


# SQL untuk Excel
database = MySQLdb.connect(
    user='root', password='root', host='localhost', database='toppgun')

app = Flask(__name__)

app.config['SECRET_KEY'] = 'kygcdjkddsfiusdlinsdiuodlnkvsbaf'
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:root@localhost:3306/toppgun'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

login_manager.login_view = 'login' #mengarahkan ke def login kalo masuk profile tanpa login

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
    post_wbs_level2 = db.Column(db.String(300))
    post_wbs_level3 = db.Column(db.String(300))
    post_judul = db.Column(db.String(300))
    post_deskripsi = db.Column(db.Text)
    post_jenis_toppgun = db.Column(db.String(300))
    post_kategori_lean = db.Column(db.String(300))
    post_file_url = db.Column(db.String(300))
    post_wbs_terkait = db.Column(db.Text)
    post_date = db.Column(db.DateTime)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

################ WTF FORM #####################

class AddUserForm(FlaskForm):
    nama = StringField('Full Name :', validators=[InputRequired('Full name is required'), length(max=100, message='Character can\'t be more than 100')])
    username = StringField('Username :', validators=[InputRequired('Username is required'), length(max=30, message='Characters can\'t be more than 30')])
    password = PasswordField('Password :', validators=[InputRequired('Password is required')])
    select_divisi = SelectField('select_divisi', choices=[('1','Gedung'),('2','Infra 1'),('3','Infra 2'),('4','EPC')])
    select_status = SelectField('select_status', choices=[(1 ,'Admin'),(2,'User')])

    select_kategori_wbs = SelectField('select_kategori_wbs', choices=[])
    select_wbs_spesifik = SelectField('select_wbs_spesifik', choices=[])
    select_wbs_level2 = SelectField('select_wbs_level2', choices=[])
    select_wbs_level3 = SelectField('select_wbs_level3', choices=[])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    username = StringField('Username :', validators=[InputRequired('Username is required'), length(max=30, message='Characters can\'t be more than 30')])
    password = PasswordField('Password :', validators=[InputRequired('Password is required')])
    remember = BooleanField('Remember Me')

# class InputForm(FlaskForm):
#     nama = StringField('Full Name :', validators=[InputRequired('Full name is required'), length(max=100, message='Character can\'t be more than 100')])
#     username = StringField('Username :', validators=[InputRequired('Username is required'), length(max=30, message='Characters can\'t be more than 30')])
#     password = PasswordField('Password :', validators=[InputRequired('Password is required')])
#     # kategori_lean = QuerySelectMultipleField(query_factory=kategori_lean_query, allow_blank=True)

class InputForm(FlaskForm):
    select_kategori_wbs = SelectField('select_kategori_wbs', choices=[])
    select_wbs_spesifik = SelectField('select_wbs_spesifik', choices=[])
    select_wbs_level2 = SelectField('select_wbs_level2', choices=[])
    select_wbs_level3 = SelectField('select_wbs_level3', choices=[])
    select_jenis_toppgun = SelectField('select_jenis_toppgun', choices=[("1", "Inovasi"),("2", "Technology")])
    select_kategori_lean = SelectField('select_kategori_lean', choices=[("1", "Defect"),("2", "Waste")])

################ ROUTE #####################

@app.route('/')
def index():
    form = LoginForm()

    return render_template('index.html', form=form)


@app.route('/login', methods=['POST','GET'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        user = User.query.filter_by(username=form.username.data).first()

        if not user:
            return render_template('index.html', form=form, message='Login Required')

        if check_password_hash (user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            return redirect(url_for('profile'))

        return render_template('index.html', form=form, message='Login Failed!')

    return render_template('index.html', form=form)

@app.route('/profile')
@login_required
def profile():

    user_id_kategori_wbs = current_user.kategori_wbs
    user_kategori_wbs = KategoriWbs.query.filter_by(id_kategori_wbs=user_id_kategori_wbs).first()

    user_id_wbs_spesifik = current_user.wbs_spesifik
    user_wbs_spesifik = WbsSpesifik.query.filter_by(id_wbs_spesifik=user_id_wbs_spesifik).first()

    # user_wbs_level2 = WbsLevel2.query.filter_by(id_wbs_level2=user_id_wbs_spesifik).first()

    # form = InputForm()
    # form.select_kategori_wbs.choices = [
    #     ("", "---")]+[(i.id_kategori_wbs, i.kategori_wbs) for i in KategoriWbs.query.all()]

    form = InputForm()
    form.select_wbs_level2.choices = [
        ("", "---")]+[(i.id_wbs_level2, i.wbs_level2) for i in WbsLevel2.query.filter_by(id_wbs_spesifik=user_id_wbs_spesifik).all()]

    results = db.session.query(InputWbs, WbsLevel3, WbsLevel2, WbsSpesifik, KategoriWbs).select_from(
        InputWbs).join(WbsLevel3).join(WbsLevel2).join(WbsSpesifik).join(KategoriWbs).all()

    return render_template('profile.html',current_user=current_user, user_kategori_wbs=user_kategori_wbs, user_wbs_spesifik=user_wbs_spesifik, form=form)


# class WbsLevel2(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     id_wbs_level2 = db.Column(db.String(50), unique=True, nullable=False)
#     wbs_level2 = db.Column(db.String(50))
#     id_wbs_spesifik = db.Column(db.String(50))

#     link_wbs_level2 = db.relationship(
#         'InputWbs', backref='wbs_level2', lazy='dynamic')


@app.route('/summary')
@login_required
def summary():

    return render_template('summary.html')

@app.route('/settings' , methods=['GET','POST'])
@login_required
def settings():

    user_status = current_user.status

    if user_status != 1 :
        return render_template('summary.html')

    else :

        form = AddUserForm()

        form.select_kategori_wbs.choices = [
            ("", "---")]+[(i.id_kategori_wbs, i.kategori_wbs) for i in KategoriWbs.query.all()]

        results = db.session.query(InputWbs, WbsLevel3, WbsLevel2, WbsSpesifik, KategoriWbs).select_from(
            InputWbs).join(WbsLevel3).join(WbsLevel2).join(WbsSpesifik).join(KategoriWbs).all()

        if request.method == 'POST':
        
            new_user = User(nama=form.nama.data, username=form.username.data, password=generate_password_hash(form.password.data), join_date=datetime.now(), divisi=form.select_divisi.data, kategori_wbs=form.select_kategori_wbs.data, wbs_spesifik=form.select_wbs_spesifik.data, status=form.select_status.data)
            db.session.add(new_user)
            db.session.commit()

            return 'sukses'

        return render_template('settings.html',form=form, results=results)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/addnewuser', methods=['GET','POST'])
@login_required
def addnewuser():
    # form = AddUserForm()



    return render_template('settings.html',form=form)


@app.route('/edit')
@login_required
def edit():

    return

@app.route('/delete')
@login_required
def delete():

    return

#################### FUNGSI IMPORT EXCEL ####################


@app.route('/importreference', methods=['POST'])
@login_required
def importreference():

    if request.method == 'POST':
        fileuploaded = request.form['source']

        # Open the workbook and define the worksheet
        book = xlrd.open_workbook(fileuploaded)
        sheet_infra = book.sheet_by_name("infra")
        sheet_gedung = book.sheet_by_name("gedung")

        # Get the cursor, which is used to traverse the database, line by line
        cursor = database.cursor()
        
        ####### INFRA ###########

        # KATEGORI WBS INFRA

        query_infra_kategori_wbs = """ REPLACE INTO kategori_wbs (id_kategori_wbs,kategori_wbs) VALUES (%s, %s)"""

        for i in range(1, sheet_infra.nrows):
            
            id_kategori_wbs = sheet_infra.cell(i, 0).value
            kategori_wbs = sheet_infra.cell(i, 1).value

            # Assign values from each row
            values_infra_kategori_wbs = (id_kategori_wbs, kategori_wbs)

            # Execute sql Query
            cursor.execute(query_infra_kategori_wbs, values_infra_kategori_wbs)


        # WBS SPESIFIK INFRA
        
        query_infra_wbs_spesifik = """ REPLACE INTO wbs_spesifik (id_wbs_spesifik,wbs_spesifik,id_kategori_wbs) VALUES (%s, %s, %s)"""
    
        for i in range(1, sheet_infra.nrows):
            id_wbs_spesifik = sheet_infra.cell(i, 2).value
            wbs_spesifik = sheet_infra.cell(i, 3).value
            id_kategori_wbs = sheet_infra.cell(i, 0).value

            # Assign values from each row
            values_infra_wbs_spesifik = (
                id_wbs_spesifik, wbs_spesifik, id_kategori_wbs)

            # Execute sql Query
            cursor.execute(query_infra_wbs_spesifik, values_infra_wbs_spesifik)

        # WBS LEVEL 2 INFRA
        
        query_infra_wbs_level2 = """ REPLACE INTO wbs_level2 (id_wbs_level2,wbs_level2,id_wbs_spesifik) VALUES (%s, %s, %s)"""

        for i in range(1, sheet_infra.nrows):
            id_wbs_level2 = sheet_infra.cell(i, 4).value
            wbs_level2 = sheet_infra.cell(i, 5).value
            id_wbs_spesifik = sheet_infra.cell(i, 2).value

            # Assign values from each row
            values_infra_wbs_level2 = (
                id_wbs_level2, wbs_level2, id_wbs_spesifik)

            # Execute sql Query
            cursor.execute(query_infra_wbs_level2, values_infra_wbs_level2)

        # WBS LEVEL 3 INFRA
        
        query_infra_wbs_level3 = """ REPLACE INTO wbs_level3 (id_wbs_level3,wbs_level3,id_wbs_level2) VALUES (%s, %s, %s)"""

        for i in range(1, sheet_infra.nrows):
            id_wbs_level3 = sheet_infra.cell(i, 6).value
            wbs_level3 = sheet_infra.cell(i, 7).value
            id_wbs_level2 = sheet_infra.cell(i, 4).value

            # Assign values from each row
            values_infra_wbs_level3 = (
                id_wbs_level3, wbs_level3, id_wbs_level2)

            # Execute sql Query
            cursor.execute(query_infra_wbs_level3, values_infra_wbs_level3)

        ####### GEDUNG ###########

        # KATEGORI WBS GEDUNG
        
        query_gedung_kategori_wbs = """ REPLACE INTO kategori_wbs (id_kategori_wbs,kategori_wbs) VALUES (%s, %s)"""

        for i in range(1, sheet_gedung.nrows):
            id_kategori_wbs = sheet_gedung.cell(i, 0).value
            kategori_wbs = sheet_gedung.cell(i, 1).value

            # Assign values from each row
            values_gedung_kategori_wbs = (id_kategori_wbs, kategori_wbs)

            # Execute sql Query
            cursor.execute(query_gedung_kategori_wbs, values_gedung_kategori_wbs)
 

        # WBS SPESIFIK GEDUNG
        
        query_gedung_wbs_spesifik = """ REPLACE INTO wbs_spesifik (id_wbs_spesifik,wbs_spesifik,id_kategori_wbs) VALUES (%s, %s, %s)"""

        for i in range(1, sheet_gedung.nrows):
            id_wbs_spesifik = sheet_gedung.cell(i, 2).value
            wbs_spesifik = sheet_gedung.cell(i, 3).value
            id_kategori_wbs = sheet_gedung.cell(i, 0).value

            # Assign values from each row
            values_gedung_wbs_spesifik = (
                id_wbs_spesifik, wbs_spesifik, id_kategori_wbs)

            # Execute sql Query
            cursor.execute(query_gedung_wbs_spesifik, values_gedung_wbs_spesifik)
 

        # WBS LEVEL 2 GEDUNG
        
            query_gedung_wbs_level2 = """ REPLACE INTO wbs_level2 (id_wbs_level2,wbs_level2,id_wbs_spesifik) VALUES (%s, %s, %s)"""

            for i in range(1, sheet_gedung.nrows):
                id_wbs_level2 = sheet_gedung.cell(i, 4).value
                wbs_level2 = sheet_gedung.cell(i, 5).value
                id_wbs_spesifik = sheet_gedung.cell(i, 2).value

                # Assign values from each row
                values_gedung_wbs_level2 = (
                    id_wbs_level2, wbs_level2, id_wbs_spesifik)

                # Execute sql Query
                cursor.execute(query_gedung_wbs_level2, values_gedung_wbs_level2)
                

        # WBS LEVEL 3 GEDUNG
        
        query_gedung_wbs_level3 = """ REPLACE INTO wbs_level3 (id_wbs_level3,wbs_level3,id_wbs_level2) VALUES (%s, %s, %s)"""

        for i in range(1, sheet_gedung.nrows):
            id_wbs_level3 = sheet_gedung.cell(i, 6).value
            wbs_level3 = sheet_gedung.cell(i, 7).value
            id_wbs_level2 = sheet_gedung.cell(i, 4).value

            # Assign values from each row
            values_gedung_wbs_level3 = (
                id_wbs_level3, wbs_level3, id_wbs_level2)

            # Execute sql Query
            cursor.execute(query_gedung_wbs_level3, values_gedung_wbs_level3)

        # Close the cursor
        cursor.close()

        # Commit the transaction
        database.commit()

        # Close the database connection
        # database.close()

        
        return redirect(url_for('settings'))

    ##################	BATAS IMPORT ####################

######################## JSON #####################

@app.route('/wbs_spesifik/<input_kategori_wbs>')
def wbs_spesifik_by_kategori_wbs(input_kategori_wbs):
    all_wbs_spesifik = WbsSpesifik.query.filter_by(
        id_kategori_wbs=input_kategori_wbs).all()

    wbs_spesifikArray = []
    for wbs_spesifik in all_wbs_spesifik:
        wbs_spesifikObj = {}
        wbs_spesifikObj['id'] = wbs_spesifik.id_wbs_spesifik
        wbs_spesifikObj['name'] = wbs_spesifik.wbs_spesifik
        wbs_spesifikArray.append(wbs_spesifikObj)

    return jsonify({'wbs_spesifik_kategori_wbs': wbs_spesifikArray})
    # return "{}".format(all_wbs_spesifik)


@app.route('/wbs_level2/<input_wbs_spesifik>')
def wbs_level2_by_wbs_spesifik(input_wbs_spesifik):
    all_wbs_level2 = WbsLevel2.query.filter_by(
        id_wbs_spesifik=input_wbs_spesifik).all()

    wbs_level2Array = []
    for wbs_level2 in all_wbs_level2:
        wbs_level2Obj = {}
        wbs_level2Obj['id'] = wbs_level2.id_wbs_level2
        wbs_level2Obj['name'] = wbs_level2.wbs_level2
        wbs_level2Array.append(wbs_level2Obj)

    return jsonify({'wbs_level2_wbs_spesifik': wbs_level2Array})


@app.route('/wbs_level3/<input_wbs_level2>')
def wbs_level3_by_wbs_level2(input_wbs_level2):
    all_wbs_level3 = WbsLevel3.query.filter_by(
        id_wbs_level2=input_wbs_level2).all()

    wbs_level3Array = []
    for wbs_level3 in all_wbs_level3:
        wbs_level3Obj = {}
        wbs_level3Obj['id'] = wbs_level3.id_wbs_level3
        wbs_level3Obj['name'] = wbs_level3.wbs_level3
        wbs_level3Array.append(wbs_level3Obj)

    return jsonify({'wbs_level3_wbs_spesifik': wbs_level3Array})

###################### END JSON ###################




if __name__ == '__main__':
    app.run(debug=True)

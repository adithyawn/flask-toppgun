from app import app, db, database, files
from models import User, KategoriWbs, WbsSpesifik, WbsLevel2, WbsLevel3, InputWbs, JenisToppgun, KategoriLean, Divisi, Post
from forms import AddUserForm, LoginForm, InputForm

from flask import render_template, redirect, url_for, json, jsonify, request

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user

from flask_uploads import UploadSet, configure_uploads

import xlrd

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

    #Buat default query untuk choice
    form.select_kategori_wbs.choices =[(user_kategori_wbs.id_kategori_wbs, user_kategori_wbs.kategori_wbs)]
    form.select_wbs_spesifik.choices =[(user_wbs_spesifik.id_wbs_spesifik, user_wbs_spesifik.wbs_spesifik)]

    # results = db.session.query(InputWbs, WbsLevel3, WbsLevel2, WbsSpesifik, KategoriWbs).select_from(
    #     InputWbs).join(WbsLevel3).join(WbsLevel2).join(WbsSpesifik).join(KategoriWbs).all()

    results = db.session.query(InputWbs, WbsLevel3, WbsLevel2, WbsSpesifik, KategoriWbs).select_from(
        InputWbs).join(WbsLevel3).join(WbsLevel2).join(WbsSpesifik).join(KategoriWbs).all()

    return render_template('profile.html',current_user=current_user, user_kategori_wbs=user_kategori_wbs, user_wbs_spesifik=user_wbs_spesifik, form=form, results=results)


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

@app.route('/submitform', methods=['POST'])
@login_required
def submitform():
    form = InputForm()

    user_id = current_user.id
    user_kategori_wbs = current_user.kategori_wbs
    user_wbs_spesifik = current_user.wbs_spesifik

    if request.method == 'POST':
        file_name = files.save(form.upload_file.data)
        file_url = files.url(file_name)

        new_post = Post(user_id=user_id, post_kategori_wbs=user_kategori_wbs, post_wbs_spesifik=current_user.wbs_spesifik, post_wbs_level2=form.select_wbs_level2.data, post_wbs_level3=form.select_wbs_level3.data, post_judul=form.judul.data, post_deskripsi=form.deskripsi.data, post_jenis_toppgun= form.select_jenis_toppgun.data, post_kategori_lean=form.select_kategori_lean.data, post_file_url=file_url,post_wbs_terkait=form.sebutkan.data, post_date=datetime.now())

        db.session.add(new_post)
        db.session.commit()

        return redirect('profile')

    return render_template('profile.html',form=form)


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

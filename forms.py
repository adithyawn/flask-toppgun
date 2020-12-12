from flask_wtf import FlaskForm
from wtforms import StringField, FileField, PasswordField, SelectField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, length, DataRequired

from flask_wtf.file import FileField, FileAllowed

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
    
class InputForm(FlaskForm):
    select_kategori_wbs = SelectField('select_kategori_wbs', choices=[])
    select_wbs_spesifik = SelectField('select_wbs_spesifik', choices=[])
    select_wbs_level2 = SelectField('select_wbs_level2', choices=[])
    select_wbs_level3 = SelectField('select_wbs_level3', choices=[])
    judul = TextAreaField()
    deskripsi = TextAreaField()
    select_jenis_toppgun = SelectField('select_jenis_toppgun', choices=[("1", "Inovasi"),("2", "Technology")])
    select_kategori_lean = SelectField('select_kategori_lean', choices=[("1", "Defect"),("2", "Waste")])
    upload_file = FileField(validators=[FileAllowed(('pdf','pptx'), 'Hanya diperbolehkan format pdf atau ppt')])
    sebutkan = TextAreaField()

################ ROUTE #####################
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    remember = BooleanField('Beni Hatırla')
    submit = SubmitField('Giriş Yap')

class RegistrationForm(FlaskForm):
    name = StringField('Ad Soyad', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Şifreyi Onayla', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Rol', choices=[('resident', 'Sakin'), ('manager', 'Yönetici')], validators=[DataRequired()])
    apartment_no = StringField('Daire No')
    submit = SubmitField('Kayıt Ol')

class AnnouncementForm(FlaskForm):
    title = StringField('Başlık', validators=[DataRequired()])
    content = TextAreaField('İçerik', validators=[DataRequired()])
    submit = SubmitField('Yayınla')

class MaintenanceRequestForm(FlaskForm):
    subject = StringField('Konu', validators=[DataRequired()])
    description = TextAreaField('Açıklama', validators=[DataRequired()])
    submit = SubmitField('Gönder')

class DueForm(FlaskForm):
    resident_id = SelectField('Sakin', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Tutar (TL)', validators=[DataRequired()])
    period = StringField('Dönem (Örn: Mayıs 2026)', validators=[DataRequired()])
    submit = SubmitField('Aidat Ata')

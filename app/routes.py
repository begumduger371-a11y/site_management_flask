from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User, Announcement, MaintenanceRequest, Due
from app.forms import LoginForm, RegistrationForm, AnnouncementForm, MaintenanceRequestForm, DueForm
import os
import google.generativeai as genai

def register_routes(app):

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                flash(f'Hoş geldiniz, {user.name}!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Giriş başarısız. E-posta veya şifre hatalı.', 'danger')
        return render_template('login.html', title='Giriş Yap', form=form)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(
                name=form.name.data,
                email=form.email.data,
                password_hash=hashed_pw,
                role=form.role.data,
                apartment_no=form.apartment_no.data or None
            )
            db.session.add(user)
            db.session.commit()
            flash('Hesabınız oluşturuldu! Giriş yapabilirsiniz.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', title='Kayıt Ol', form=form)

    @app.route('/logout')
    def logout():
        logout_user()
        flash('Başarıyla çıkış yapıldı.', 'info')
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        announcements = Announcement.query.order_by(Announcement.date.desc()).limit(5).all()
        if current_user.role == 'manager':
            requests = MaintenanceRequest.query.order_by(MaintenanceRequest.date.desc()).limit(5).all()
            residents = User.query.filter_by(role='resident').all()
            pending_count = MaintenanceRequest.query.filter_by(status='pending').count()
            in_progress_count = MaintenanceRequest.query.filter_by(status='in_progress').count()
            done_count = MaintenanceRequest.query.filter_by(status='completed').count()
            total_dues = db.session.query(db.func.sum(Due.amount)).scalar() or 0
            paid_dues = db.session.query(db.func.sum(Due.amount)).filter_by(is_paid=True).scalar() or 0
            unpaid_dues = total_dues - paid_dues
            return render_template('dashboard.html',
                announcements=announcements, requests=requests,
                residents=residents, pending_count=pending_count,
                in_progress_count=in_progress_count, done_count=done_count,
                total_dues=total_dues, paid_dues=paid_dues, unpaid_dues=unpaid_dues)
        else:
            my_requests = MaintenanceRequest.query.filter_by(user_id=current_user.id).order_by(MaintenanceRequest.date.desc()).limit(5).all()
            my_dues = Due.query.filter_by(user_id=current_user.id).order_by(Due.id.desc()).all()
            unpaid = sum(d.amount for d in my_dues if not d.is_paid)
            paid = sum(d.amount for d in my_dues if d.is_paid)
            return render_template('dashboard.html',
                announcements=announcements, my_requests=my_requests,
                my_dues=my_dues, unpaid=unpaid, paid=paid)

    @app.route('/announcements')
    @login_required
    def announcements():
        all_ann = Announcement.query.order_by(Announcement.date.desc()).all()
        form = AnnouncementForm() if current_user.role == 'manager' else None
        return render_template('announcements.html', title='Duyurular', announcements=all_ann, form=form)

    @app.route('/announcements/new', methods=['POST'])
    @login_required
    def new_announcement():
        if current_user.role != 'manager':
            abort(403)
        form = AnnouncementForm()
        if form.validate_on_submit():
            ann = Announcement(title=form.title.data, content=form.content.data, author_id=current_user.id)
            db.session.add(ann)
            db.session.commit()
            flash('Duyuru başarıyla yayınlandı!', 'success')
        return redirect(url_for('announcements'))

    @app.route('/announcements/<int:ann_id>/delete', methods=['POST'])
    @login_required
    def delete_announcement(ann_id):
        if current_user.role != 'manager':
            abort(403)
        ann = Announcement.query.get_or_404(ann_id)
        db.session.delete(ann)
        db.session.commit()
        flash('Duyuru silindi.', 'info')
        return redirect(url_for('announcements'))

    @app.route('/requests')
    @login_required
    def maintenance_requests():
        form = MaintenanceRequestForm()
        if current_user.role == 'manager':
            reqs = MaintenanceRequest.query.order_by(MaintenanceRequest.date.desc()).all()
        else:
            reqs = MaintenanceRequest.query.filter_by(user_id=current_user.id).order_by(MaintenanceRequest.date.desc()).all()
        return render_template('requests.html', title='Arıza Bildirimleri', requests=reqs, form=form)

    @app.route('/requests/new', methods=['POST'])
    @login_required
    def new_request():
        if current_user.role == 'manager':
            abort(403)
        form = MaintenanceRequestForm()
        if form.validate_on_submit():
            req = MaintenanceRequest(
                user_id=current_user.id,
                subject=form.subject.data,
                description=form.description.data
            )
            db.session.add(req)
            db.session.commit()
            flash('Arıza bildirimi gönderildi!', 'success')
        return redirect(url_for('maintenance_requests'))

    @app.route('/requests/<int:req_id>/status', methods=['POST'])
    @login_required
    def update_request_status(req_id):
        if current_user.role != 'manager':
            abort(403)
        req = MaintenanceRequest.query.get_or_404(req_id)
        new_status = request.form.get('status')
        if new_status in ['pending', 'in_progress', 'completed']:
            req.status = new_status
            db.session.commit()
            flash('Arıza durumu güncellendi.', 'success')
        return redirect(url_for('maintenance_requests'))

    @app.route('/dues')
    @login_required
    def dues():
        if current_user.role == 'manager':
            form = DueForm()
            form.resident_id.choices = [(u.id, f"{u.name} — Daire {u.apartment_no or 'Belirtilmemiş'}") 
                                         for u in User.query.filter_by(role='resident').all()]
            all_dues = Due.query.order_by(Due.id.desc()).all()
            return render_template('dues.html', title='Aidatlar', dues=all_dues, form=form)
        else:
            my_dues = Due.query.filter_by(user_id=current_user.id).order_by(Due.id.desc()).all()
            return render_template('dues.html', title='Aidatlarım', dues=my_dues, form=None)

    @app.route('/dues/new', methods=['POST'])
    @login_required
    def new_due():
        if current_user.role != 'manager':
            abort(403)
        form = DueForm()
        form.resident_id.choices = [(u.id, u.name) for u in User.query.filter_by(role='resident').all()]
        if form.validate_on_submit():
            due = Due(
                user_id=form.resident_id.data,
                amount=float(form.amount.data),
                period=form.period.data
            )
            db.session.add(due)
            db.session.commit()
            flash('Aidat başarıyla atandı!', 'success')
        return redirect(url_for('dues'))

    @app.route('/dues/<int:due_id>/pay', methods=['POST'])
    @login_required
    def pay_due(due_id):
        due = Due.query.get_or_404(due_id)
        if current_user.role == 'resident' and due.user_id != current_user.id:
            abort(403)
        due.is_paid = True
        db.session.commit()
        flash(f'{due.period} dönemi aidatı ödendi ✅', 'success')
        return redirect(url_for('dues'))

    # ─────────────────── AKILLI ASİSTAN (GEMINI INTEGRATION) ───────────────────
    @app.route('/smart-assistant', methods=['GET', 'POST'])
    @login_required
    def smart_assistant():
        ai_response = None
        if request.method == 'POST':
            user_input = request.form.get('user_description')
            category = request.form.get('issue_category')
            if user_input:
                try:
                    api_key = os.environ.get('GEMINI_API_KEY')
                    if not api_key:
                        flash('API Anahtarı bulunamadı. Lütfen .env dosyasını kontrol edin.', 'danger')
                        return render_template('smart_assistant.html', title='Akıllı Asistan', ai_response=None)
                    
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    
                    prompt = f"Sen akıllı site yönetim asistanısın. Kullanıcı '{category}' kategorisinde şu sorunu iletti: '{user_input}'. Bu duruma yönelik acil yapılması gerekenleri, İSG risk analizini ve çözüm önerilerini profesyonel ve net bir Türkçe ile listele."
                    response = model.generate_content(prompt)
                    ai_response = response.text
                    flash('Gemini Asistanı talebi başarıyla analiz etti!', 'success')
                except Exception as e:
                    flash(f'Yapay zeka hatası: {str(e)}', 'danger')
        return render_template('smart_assistant.html', title='Akıllı Asistan', ai_response=ai_response)

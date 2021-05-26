from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import db, User, Room, Note, UserRelation, Message, Participant
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


profile = Blueprint('profile', __name__)


@profile.route('/profile/change-username', methods=['GET', 'POST'])
def change_username():
    if request.method == 'POST':
        username = request.form.get('username')
        if username == '' or username == None:
            flash('Podaj nową nazwę użytkownika!', category='error')
        else:
            if len(username) < 3:
                flash('Nowa nazwa użytkownika jest zbyt krótka!', category='error')
            else:
                user = User.query.filter_by(username=username)
                if user:
                    flash('Istnieje użytkownik o takiej nazwie!', category='error')
                else:
                    user = User.query.filter_by(user_id=current_user.user_id).first()
                    user.username = username
                    db.session.commit()
                    flash('Nazwa użytkownika została!', category='success')
                    return redirect(url_for('views.profile'))

    return render_template("profile/change_username.html", user=current_user)


@profile.route('/profile/change-image', methods=['GET', 'POST'])
def change_image():
    if request.method == 'POST':
        print(request.files)
        if 'image' not in request.files:
            flash('No file part', category='error')
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No selected file', category='error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            extension = filename.rsplit('.', 1)[1].lower()
            unique_filename = uuid.uuid4().hex

            filename = unique_filename + '.' + extension

            #########################################
            #####        ZMIENIC SCIEZKE        #####
            #########################################
            file.save(os.path.join('C:\\Users\\grzeg\\OneDrive - The Opole University of Technology\\Projekt Zespołowy Systemu Informatycznego\\PZSI-I.S.1st.6-20-21L\\application\\static\\images\\user', filename))

            user = User.query.filter_by(user_id=current_user.user_id).first()
            user.image_path = '/static/images/user/' + filename
            db.session.commit()
            return redirect(url_for('views.profile'))
    return render_template("profile/change_image.html", user=current_user)


@profile.route('/profile/change-password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old-password')
        new_password = request.form.get('new-password')
        confirm_password = request.form.get('confirm-password')

        if check_password_hash(current_user.password, old_password):
            if new_password == None or confirm_password == None:
                flash('Wpisz nowe hasło', category='error')
            else:
                if new_password != confirm_password:
                    flash('Nowe hasło musi być takie samo', category='error')
                else:
                   if old_password == new_password:
                       flash('Nowe i stare hasła nie mogą być takie same', category='error')
                   else:
                       if len(new_password) < 8:
                           flash('Nowe hasło jest zbyt krótkie', category='error')
                       else:
                           user = User.query.filter_by(user_id=current_user.user_id)
                           user.password = generate_password_hash(new_password, method='sha256')
                           db.session.commit()
                           flash('Hasło zostało zmienione!', category='success')
                           return redirect(url_for('views.profile'))
        else:
            flash('Nie poprawne hasło', category='error')

    return render_template("profile/change_password.html", user=current_user)


@profile.route('/profile/change-email', methods=['GET', 'POST'])
def change_email():
    if request.method == 'POST':
        email = request.form.get('email')
        if email == '' or email == None:
            flash('Podaj nowy adres Email!', category='error')
        else:
            if len(email) < 8:
                flash('Nowy adres email jest zbyt krótki!', category='error')
            else:
                print(email)
                user = User.query.filter_by(email=email).first()
                print(user)
                if user:
                    flash('Istnieje użytkownik o takim adresie email!', category='error')
                else:
                    user = User.query.filter_by(user_id=current_user.user_id).first()
                    user.email = email
                    db.session.commit()
                    flash('Adres Email został zmieniony!', category='success')
                    return redirect(url_for('views.profile'))

    return render_template("profile/change_email.html", user=current_user)


@profile.route('/profile/delete-account', methods=['GET', 'POST'])
def delete_account():
    if request.method == 'POST':
        user = User.query.filter_by(user_id=current_user.user_id).first()
        db.session.delete(user)
        db.session.commit()
        flash('Konto zostało usunięte', category='success')
        return redirect('/logout')

    return render_template("profile/delete_account.html", user=current_user)

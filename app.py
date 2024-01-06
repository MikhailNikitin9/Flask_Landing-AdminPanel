from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3
import hashlib
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Замените на ваш секретный ключ

# Путь для сохранения изображений
path_to_save_images = os.path.join(app.root_path, 'static', 'imgs')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    conn = get_db_connection()
    blocks = conn.execute('SELECT * FROM content').fetchall()  # Получаем все записи из таблицы content
    conn.close()

    # Преобразование данных из БД в список словарей
    blocks_list = [dict(ix) for ix in blocks]
    # print(blocks_list) [{строка 1 из бд},{строка 2 из бд},{строка 3 из бд}, строка 4 из бд]

     # Теперь нужно сделать группировку списка в один словарь json
    # Группировка данных в словарь JSON
    json_data = {}
    for raw in blocks_list:
        # Создание новой записи, если ключ еще не существует
        if raw['idblock'] not in json_data:
            json_data[raw['idblock']] = []

        # Добавление данных в существующий ключ
        json_data[raw['idblock']].append({
            'id': raw['id'],
            'short_title': raw['short_title'],
            'img': raw['img'],
            'altimg': raw['altimg'],
            'title': raw['title'],
            'contenttext': raw['contenttext'],
            'author': raw['author'],
            'timestampdata': raw['timestampdata']
        })
    # далее передаем json_data на фронт
    return render_template('landing.html', json_data=json_data)

@app.route('/adm_login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        print(user)

        if user and user['password'] == hashed_password:
            session['user_id'] = user['id']
            print('yes')
            return redirect(url_for('admin_panel'))

        else:
            error = 'Неправильное имя пользователя или пароль'

    return render_template('login_adm.html', error=error)

@app.route('/logout')
def logout():
    # Удаление данных пользователя из сессии
    session.clear()
    # Перенаправление на главную страницу или страницу входа
    return redirect(url_for('home'))



@app.route('/update_content', methods=['POST'])
def update_content():

    content_id = request.form['id']
    short_title = request.form['short_title']
    title = request.form['title']
    altimg = request.form['altimg']
    contenttext = request.form['contenttext']

    # Обработка загруженного файла
    file = request.files['img']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(path_to_save_images, filename)
        imgpath = "/static/imgs/"+filename
        file.save(save_path)
        # Обновите путь изображения в вашей базе данных

    # Обновление данных в базе
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if file:
        cursor.execute('UPDATE content SET short_title=?, img=?, altimg=?, title=?, contenttext=? WHERE id=?',
                   (short_title, imgpath, altimg, title, contenttext, content_id))
    else:
        cursor.execute('UPDATE content SET short_title=?, altimg=?, title=?, contenttext=? WHERE id=?',
                       (short_title, altimg, title, contenttext, content_id))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_panel'))



@app.route('/admin_panel')
def admin_panel():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    blocks = conn.execute('SELECT * FROM content').fetchall()  # Получаем все записи из таблицы content
    conn.close()

    # Преобразование данных из БД в список словарей
    blocks_list = [dict(ix) for ix in blocks]
    # print(blocks_list) [{строка 1 из бд},{строка 2 из бд},{строка 3 из бд}, строка 4 из бд]

     # Теперь нужно сделать группировку списка в один словарь json
    # Группировка данных в словарь JSON
    json_data = {}
    for raw in blocks_list:
        # Создание новой записи, если ключ еще не существует
        if raw['idblock'] not in json_data:
            json_data[raw['idblock']] = []

        # Добавление данных в существующий ключ
        json_data[raw['idblock']].append({
            'id': raw['id'],
            'short_title': raw['short_title'],
            'img': raw['img'],
            'altimg': raw['altimg'],
            'title': raw['title'],
            'contenttext': raw['contenttext'],
            'author': raw['author'],
            'timestampdata': raw['timestampdata']
        })

    # print(json_data)
    # передаем на json на фронт - далее нужно смотреть admin_panel.html и обрабатывать там
    return render_template('admin_panel.html', json_data=json_data)

if __name__ == '__main__':
    app.run(debug=True)

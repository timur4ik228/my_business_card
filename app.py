# app.py
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Таблица для визитки
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS business_card (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT,
            company TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            about TEXT,
            skills TEXT
        )
    ''')
    
    # Таблица для статистики посещений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS site_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visit_date TEXT NOT NULL,
            ip_address TEXT
        )
    ''')
    
    # Проверяем, есть ли уже данные визитки
    cursor.execute('SELECT COUNT(*) FROM business_card')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO business_card 
            (name, position, company, email, phone, address, about, skills)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'Иван Иванов',
            'Веб-разработчик',
            'Моя компания',
            'ivan@example.com',
            '+7 (123) 456-78-90',
            'Москва, ул. Примерная, 123',
            'Я профессиональный веб-разработчик с опытом работы более 5 лет.',
            'HTML, CSS, JavaScript, Python, Flask'
        ))
    
    conn.commit()
    conn.close()

init_db()
# app.py (продолжение)
def record_visit():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        ip_address = request.remote_addr
        cursor.execute('''
            INSERT INTO site_stats (visit_date, ip_address)
            VALUES (?, ?)
        ''', (datetime.now().isoformat(), ip_address))
        conn.commit()
    except Exception as e:
        print(f"Error recording visit: {e}")
    finally:
        conn.close()

@app.route('/')
def index():
    # Записываем посещение
    record_visit()
    
    # Получаем данные визитки
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM business_card LIMIT 1')
    card_data = cursor.fetchone()
    
    # Получаем статистику посещений
    cursor.execute('SELECT COUNT(*) FROM site_stats')
    visit_count = cursor.fetchone()[0]
    
    # Получаем уникальные посещения (по IP)
    cursor.execute('SELECT COUNT(DISTINCT ip_address) FROM site_stats')
    unique_visitors = cursor.fetchone()[0]
    
    conn.close()
    
    if card_data:
        keys = ['id', 'name', 'position', 'company', 'email', 'phone', 
                'address', 'about', 'skills']
        card_dict = dict(zip(keys, card_data))
        card_dict['skills_list'] = card_dict['skills'].split(', ') if card_dict['skills'] else []
        return render_template('index.html', 
                             card=card_dict,
                             visit_count=visit_count,
                             unique_visitors=unique_visitors)
    else:
        return render_template('index.html', 
                             card=None,
                             visit_count=visit_count,
                             unique_visitors=unique_visitors)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':
        # Обновляем данные в базе
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE business_card SET
            name = ?,
            position = ?,
            company = ?,
            email = ?,
            phone = ?,
            address = ?,
            about = ?,
            skills = ?
            WHERE id = 1
        ''', (
            request.form['name'],
            request.form['position'],
            request.form['company'],
            request.form['email'],
            request.form['phone'],
            request.form['address'],
            request.form['about'],
            request.form['skills']
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    # GET запрос - показать форму редактирования
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM business_card LIMIT 1')
    card_data = cursor.fetchone()
    conn.close()
    
    if card_data:
        keys = ['id', 'name', 'position', 'company', 'email', 'phone', 
                'address', 'about', 'skills']
        card_dict = dict(zip(keys, card_data))
        return render_template('edit.html', card=card_dict)
    else:
        return render_template('edit.html', card=None)

if __name__ == '__main__':
    app.run(debug=True)
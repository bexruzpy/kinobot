# app.py

from flask import Flask, render_template, jsonify, request, redirect, url_for
# database.py faylingizni to'g'ri import qilganingizga ishonch hosil qiling
from database import PostgreSQLController 
from functools import wraps
import os
import dotenv
dotenv.load_dotenv(dotenv_path='../.env')

SECRET_KEY = os.getenv("SECRET_KEY")

# Flask ilovasini yaratamiz
app = Flask(__name__)

# Ma'lumotlar bazasiga ulanish
# DIQQAT: Bu yerdagi ma'lumotlar botingizdagi bilan bir xil bo'lishi shart!
db = PostgreSQLController(
    db_name='kino_db',
    user='postgres',
    password='admin1957', # O'zingizning parolingizni yozing
    host='localhost',
    port=5432
)




# --- Dekoratorlar ---

def api_key_required(f):
    """
    Maxfiy kalitni URL so'rovidan (query parameter) tekshiradigan dekorator.
    ISHlatish usuli: /api/kinolar?secret_key=sizning_kalitingiz
    ❗️ BU USUL XAVFSIZ EMAS! Faqat o'rganish uchun.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_key = request.args.get('secret_key')
        if user_key and user_key == SECRET_KEY:
            # Agar kalit to'g'ri bo'lsa, asosiy funksiyani ishga tushirish
            return f(*args, **kwargs)
        else:
            # Aks holda, xatolik qaytarish
            return jsonify({"error": "Ruxsat berilmagan. Maxfiy kalit noto'g'ri yoki kiritilmagan."}), 403
    return decorated_function


def secure_api_key_required(f):
    """
    Maxfiy kalitni HTTP sarlavhasidan (Header) tekshiradigan dekorator.
    Bu eng to'g'ri va xavfsiz usuldir.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # So'rov sarlavhalaridan 'X-API-Key' ni o'qish
        user_key = request.args.get('X-API-Key')
        if user_key and user_key == SECRET_KEY:
            # Agar kalit to'g'ri bo'lsa, asosiy funksiyani ishga tushirish
            return f(*args, **kwargs)
        else:
            # Aks holda, xatolik qaytarish
            return jsonify({"error": "Ruxsat berilmagan. 'X-API-Key' sarlavhasi noto'g'ri yoki kiritilmagan."}), 403
    return decorated_function




# Asosiy sahifa uchun marshrut (route)
@app.route('/')
@api_key_required
def admin_panel():
    """ admin.html faylini ochib beradi """
    return render_template('admin.html', secret_key=SECRET_KEY)

# --- YANGI: Tahrirlash sahifasini ko'rsatish uchun ---
@app.route('/edit/<int:kino_id>')
@api_key_required
def edit_page(kino_id):
    """ ID bo'yicha kinoni olib, tahrirlash uchun edit.html sahifasini ochadi """
    try:
        # database.py faylida ID bo'yicha bitta kinoni oladigan funksiya kerak bo'ladi
        # Masalan: get_kino_by_id(kino_id) -> (id, name, file_id)
        kino_data = db.get_kino_by_id(kino_id)
        if kino_data:
            kino = {'id': kino_data[0], 'name': kino_data[1]}
            return render_template('edit.html', kino=kino, secret_key=SECRET_KEY)
        else:
            return "Kino topilmadi", 404
    except Exception as e:
        return f"Xatolik: {str(e)}", 500

# --- YANGI: Tahrirlangan ma'lumotlarni saqlash uchun ---
@app.route('/update/<int:old_kino_id>', methods=['POST'])
@secure_api_key_required
def update_kino_post(old_kino_id):
    """ Tahrirlash sahifasidan kelgan POST so'rovni qabul qilib, bazani yangilaydi """
    try:
        new_name = request.form['name']
        new_id = int(request.form['new_id'])

        # database.py faylingizdagi 'update_kino' metodidan foydalanamiz
        db.update_kino(old_kino_id, new_name, new_id)
        
        # Bosh sahifaga qaytaramiz
        return redirect(url_for('admin_panel', secret_key=SECRET_KEY))
    except Exception as e:
        return f"Xatolik: {str(e)}", 500


# --- API Marshrutlari (Asosan bosh sahifa uchun) ---

@app.route('/api/kinolar', methods=['GET'])
@secure_api_key_required
def get_kinolar():
    """ Ma'lumotlar bazasidan barcha kinolarni oladi. file_id yuborilmaydi. """
    try:
        kinolar = db.get_all_kinos() 
        kinolar_list = [{'id': k[0], 'name': k[1]} for k in kinolar]
        return jsonify(kinolar_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/kinolar/<int:kino_id>', methods=['DELETE'])
@secure_api_key_required
def delete_kino(kino_id):
    """ ID bo'yicha kinoni o'chiradi """
    try:
        db.delete_kino_by_id(kino_id)
        return jsonify({"success": True, "message": f"{kino_id}-ID'li kino o'chirildi"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Dasturni ishga tushirish
if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")


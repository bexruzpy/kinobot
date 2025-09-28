# app.py

from flask import Flask, render_template, jsonify, request
from database import PostgreSQLController # Sizning database.py faylingizni import qilamiz

# Flask ilovasini yaratamiz
app = Flask(__name__)

# Ma'lumotlar bazasiga ulanish uchun sizning sinfingizdan obyekt olamiz
# DIQQAT: Bu yerdagi ma'lumotlar botingizdagi bilan bir xil bo'lishi shart!
db = PostgreSQLController(
    db_name='kino_db',
    user='postgres',
    password='admin1957', # O'zingizning parolingizni yozing
    host='localhost',
    port=5432
)

# Asosiy sahifa uchun marshrut (route)
@app.route('/')
def admin_panel():
    """ admin.html faylini ochib beradi """
    return render_template('admin.html')

# --- API Marshrutlari (Frontend bilan "gaplashish" uchun) ---

# Barcha kinolarni olish uchun (GET)
@app.route('/api/kinolar', methods=['GET'])
def get_kinolar():
    """ Ma'lumotlar bazasidan barcha kinolarni olib, JSON formatida qaytaradi """
    try:
        # Sizning get_all_kinos() metodidan foydalanamiz
        kinolar = db.get_all_kinos() 
        # Ma'lumotlarni qulay formatga o'tkazamiz
        kinolar_list = [{'id': k[0], 'name': k[1], 'file_id': k[2]} for k in kinolar]
        return jsonify(kinolar_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Yangi kino qo'shish uchun (POST)
@app.route('/api/kinolar', methods=['POST'])
def add_kino():
    """ Yangi kino ma'lumotlarini qabul qilib, bazaga qo'shadi """
    data = request.get_json()
    if not data or 'name' not in data or 'file_id' not in data:
        return jsonify({"error": "Kino nomi (name) va file_id yuborilishi shart!"}), 400
    
    try:
        # Sizning add_kino() metodidan foydalanamiz
        kino_id = db.add_kino(name=data['name'], file_id=data['file_id'])
        if kino_id:
            return jsonify({"success": True, "id": kino_id}), 201
        else:
            return jsonify({"error": "Bazaga qo'shishda xatolik"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Kinoni o'chirish uchun (DELETE)
@app.route('/api/kinolar/<int:kino_id>', methods=['DELETE'])
def delete_kino(kino_id):
    """ ID bo'yicha kinoni o'chiradi """
    try:
        # Sizning delete_kino_by_id() metodidan foydalanamiz
        db.delete_kino_by_id(kino_id)
        return jsonify({"success": True, "message": f"{kino_id}-ID'li kino o'chirildi"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Dasturni ishga tushirish
if __name__ == '__main__':
    app.run(debug=True, port=5000)
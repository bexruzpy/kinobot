import os
import json
from dotenv import load_dotenv

# .env faylidan o'zgaruvchilarni yuklash uchun
load_dotenv()

# .env faylidagi o'zgaruvchilarni o'qib olish
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")
SECRET_KEY = os.getenv("SECRET_KEY")

# Admin ID'larini vergul bilan ajratilgan qatordan ro'yxatga o'tkazish
# Agar ADMINS o'zgaruvchisi bo'lmasa, bo'sh ro'yxat hosil bo'ladi.
ADMINS_STR = os.getenv("ADMINS", "")
ADMINS = [int(admin_id) for admin_id in ADMINS_STR.split(',') if admin_id]
ADMIN = ADMINS[1] if ADMINS else None  # Birinchi adminni asosiy admin sifatida belgilash

# --- Kanallar bilan ishlash logikasi ---

def get_channels_from_json():
    """kanallar.json faylidan kanallar ro'yxatini o'qiydi."""
    try:
        with open("kanallar.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Agar fayl topilmasa yoki bo'sh bo'lsa, bo'sh ro'yxat qaytaradi
        return []

class Chanel:
    def __init__(self, string):
        if string.startswith("@"):
            self.id = string
            self.url = f"https://t.me/{string[1:]}"
        elif "|" in string:
            parts = string.split("|", 1)
            self.id = parts[0]
            self.url = parts[1]
        else:
            # Agar format noma'lum bo'lsa, faqat ID ni saqlaymiz
            self.id = string
            self.url = "" 

    def get_save(self):
        """Saqlash uchun qulay formatda qaytaradi."""
        return f"{self.id}|{self.url}"

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return str(self.id)

# Dastur ishga tushganda kanallarni yuklab olish
# channels_data = get_channels_from_json()
# CHANNELS = [Chanel(ch) for ch in channels_data]
def get_channels():
    with open("kanallar.json", "r", encoding="utf-8") as f:
        return json.load(f)
CHANNELS = get_channels()
# --- O'zgaruvchilar to'g'ri yuklanganini tekshirish uchun ---
# Ushbu faylni to'g'ridan-to'g'ri ishga tushirsangiz, natijalarni ko'rishingiz mumkin.
if __name__ == "__main__":
    if not all([BOT_TOKEN, BOT_USERNAME, SECRET_KEY, ADMINS]):
        print("DIQQAT: .env faylidagi ba'zi ma'lumotlar topilmadi!")
    else:
        print("✅ Barcha o'zgaruvchilar muvaffaqiyatli yuklandi.")
        print("-" * 20)
        print(f"Bot Token: ...{BOT_TOKEN[-6:]}") # Xavfsizlik uchun tokenning bir qismi
        print(f"Bot Username: {BOT_USERNAME}")
        print(f"Adminlar ro'yxati: {ADMINS}")
        print(f"Kanallar ro'yxati: {CHANNELS}")

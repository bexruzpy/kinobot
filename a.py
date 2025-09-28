from telebot import TeleBot
from telebot import types
from telebot.apihelper import ApiTelegramException
from settings import *
from utils import *
from database import PostgreSQLController


bot = TeleBot(bot_token)


# Sinfni chaqiramiz
db = PostgreSQLController(
    

db_name='kino_db',
    user='postgres',
    password='admin1957',
    host='localhost',
    port=5432
)
@bot.message_handler(commands=["start"], func=lambda x: x.from_user.id == admin and x.chat.type == "supergroup" and channels["edited"] != [])
def admin_set_channel(message):
    ch_id = message.chat.id
    try:
        res = bot.create_chat_invite_link(chat_id=ch_id)
    except ApiTelegramException:
        bot.send_message(message.chat.id, "Avval kanalga ushbu botni admin qiling.")
        return
    ch_link = res.invite_link
    text = f"{ch_link}|{ch_id}"
    if message.text.strip()[0] != "@" and not text.startswith("https://t.me/+"):
        bot.send_message(message.chat.id, "Noto'g'ri username qayta kiriting")
        return
    tur, kanal_id = map(str, channels["edited"].pop().split("_"))
    if tur == "a":
        channels["asosiy_kanllar"][f"kanal_{kanal_id}"] = text
    else:
        channels["yuklash_kanal"][f"kanal_{kanal_id}"] = text
    update_channels(channels)
    bot.send_message(message.from_user.id, "Kanal muvaffaqiyatli sozlandi 👌")
    bot.send_message(message.chat.id, "Ushbu guruh sozlandi 👌")
@bot.message_handler(func=lambda x: x.chat.type != "private")
def ignore(message):
    print(message)
@bot.message_handler(commands=["start"], func=lambda x: x.chat.id == admin and x.text.startswith("/start kanal_"))
def kanal(message):
    chat_id = message.chat.id
    kanal_id = int(message.text.split("_")[-1])
    if kanal_id > 6:
        return
    kanal = channels["asosiy_kanllar"][f"kanal_{kanal_id}"]
    markup = types.InlineKeyboardMarkup()
    if kanal != "-":
        markup.row(
            types.InlineKeyboardButton("✍️ Taxrirlash", callback_data=f"set_kanal_{kanal_id}"),
            types.InlineKeyboardButton("🗑 O'chirish", callback_data=f"delete_kanal_{kanal_id}")
        )
    else:
        markup.row(
            types.InlineKeyboardButton("✍️ Kanal kiritish", callback_data=f"set_kanal_{kanal_id}")
        )
    markup.row(types.InlineKeyboardButton("❌ Yopish", callback_data="cancel"))
    bot.send_message(chat_id, f"Majburiy obuna uchun kanal {kanal_id}\nKanal: {(kanal.split('|')[0] if kanal.startswith('https://t.me/+') else kanal) if kanal!='-' else 'sozlanmagan'}", reply_markup=markup)

@bot.message_handler(commands=["start"], func=lambda x: x.chat.id == admin and x.text.startswith("/start y_kanal_"))
def kanal(message):
    chat_id = message.chat.id
    kanal_id = int(message.text.split("_")[-1])
    if kanal_id > 6:
        return
    kanal = channels["yuklash_kanal"][f"kanal_{kanal_id}"]
    markup = types.InlineKeyboardMarkup()
    if kanal != "-":
        markup.row(
            types.InlineKeyboardButton("✍️ Taxrirlash", callback_data=f"set_ykanal_{kanal_id}"),
            types.InlineKeyboardButton("🗑 O'chirish", callback_data=f"delete_ykanal_{kanal_id}")
        )
    else:
        markup.row(
            types.InlineKeyboardButton("✍️ Kanal kiritish", callback_data=f"set_ykanal_{kanal_id}")
        )
    markup.row(types.InlineKeyboardButton("❌ Yopish", callback_data="cancel"))
    bot.send_message(chat_id, f"Yuklash uchun kanal {kanal_id}\nKanal: {(kanal.split('|')[0] if kanal.startswith('https://t.me/+') else kanal) if kanal!='-' else 'sozlanmagan'}", reply_markup=markup)


@bot.callback_query_handler(func=lambda x: x.data == "cancel")
def cancel(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
@bot.message_handler(commands=["start"])
def start(message):
    all_kinos = db.get_all_kinos()
    chat_id = message.chat.id
    if admin == message.chat.id:
        text = message.text.replace("/start", "").strip()
        print(text)
        if text != "":
            try:
                # admin uchun tugma
                markup = types.InlineKeyboardMarkup()
                del_b = types.InlineKeyboardButton("O'chirish 🗑", callback_data="delete")
                no = types.InlineKeyboardButton("Yopish ❌", callback_data="close")
                markup.row(no, del_b)
                kod = int(text[4:])
                kino = db.get_kino_by_id(kod)
                if not kino:
                    bot.send_message(chat_id=chat_id, text="Ushbu idga mos kino topilmadi")
                    return
                if chat_id == admin:
                    bot.send_video(chat_id=chat_id, video=kino[2], protect_content=True, caption=f"🎬 Nomi: {kino[1]}\n\n🔒 Kino kodi: {kino[0]}\n\nBizning kanal: {channels['glavniy_channel']}", reply_markup=markup)
                else:
                    bot.send_video(chat_id=chat_id, video=kino[2], protect_content=True, caption=f"🎬 Nomi: {kino[1]}\n\n🔒 Kino kodi: {kino[0]}\n\nBizning kanal: {channels['glavniy_channel']}")
                return
            except:
                pass
        bot.send_message(chat_id, f"Xush kelibsiz admin\n\nHozida sizda umumiy {len(all_kinos)}ta kino mavjud\n\n- Barcha kinolarni ko'rish 👉 /barchakinolar\n- Yangi kino yuklash uchun Uni izoh bilan yuboring\n\nSozlamalar 👉 /settings")
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🎧 Musiqiy premyera", url=f"https://t.me/{channels['glavniy_channel'][1:]}"))
    markup.add(types.InlineKeyboardButton(text="🔍 Kino qidirish", url="https://t.me/QASHQIRLAR_MAKONI_pistirma_full"))
    bot.send_message(chat_id, f"Assalomu alaykum {message.chat.first_name} botimizga xush kelibsiz!\n\n🔒 Kino kodini yuboring", reply_markup=markup)

@bot.message_handler(commands=["barchakinolar"])
def allkinolar(message):
    chat_id = message.chat.id
    all_kinos = db.get_all_kinos()

    if admin == message.chat.id:
        qism = ""
        for i, kino in enumerate(all_kinos):
            qism+=f"<a href=\"https://t.me/{bot_username[1:]}?start=kino{kino[0]}\">{i+1} "+kino[1].split('\n')[0].strip()[:30]+f"</a> kodi: <code>{kino[0]}</code>\n"
            if (i+1)%30 == 0:
                bot.send_message(chat_id, qism, parse_mode="html")
                qism=""
        if qism != "":
            bot.send_message(chat_id, qism, parse_mode="html")

@bot.message_handler(commands=["settings"], func=lambda x: x.chat.id == admin)
def all_settings(message):
    chat_id = message.chat.id
    all_kinos = db.get_all_kinos()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Majburiy obuna", callback_data="majburiy_obuna"))
    markup.add(types.InlineKeyboardButton(text="Yuklash uchun", callback_data="yuklash_uchun"))


    bot.send_message(chat_id, f"Assalomu alaykum {message.chat.first_name}\n\nKanallarni sozlash", reply_markup=markup)


@bot.callback_query_handler(func=lambda x: (x.data == "majburiy_obuna" and x.message.chat.id == admin))
def majburiy_obuna_kanallarni_sozlash(query):
    chat_id = query.message.chat.id
    matn = "Majburiy obuna kanallarini sozlash uchun ustiga bosing 👇\n\n"
    for key, kanal in channels["asosiy_kanllar"].items():
        matn += f"<a href=\"https://t.me/{bot_username[1:]}?start=kanal_{key}\">{key[-1]}. " + (("Shaxsiy kanal" if kanal.startswith("https://t.me/+") else kanal ) if kanal!='-' else "Qo'shish")+"</a>\n"

    bot.send_message(
        chat_id,
        matn,
        parse_mode="html"
    )   


@bot.callback_query_handler(func=lambda x: (x.data == "yuklash_uchun" and x.message.chat.id == admin))
def majburiy_obuna_kanallarni_sozlash(query):
    chat_id = query.message.chat.id
    matn = "Yuklash kanalarini sozlash uchun ustiga bosing 👇\n\n"
    for key, kanal in channels["yuklash_kanal"].items():
        matn += f"<a href=\"https://t.me/{bot_username[1:]}?start=y_kanal_{key}\">{key[-1]}. " +((kanal if kanal[0] == "@" else "Shaxsiy kanal") if kanal!='-' else "Qo\'shish")+"</a>\n"
    
    bot.send_message(
        chat_id,
        matn,
        parse_mode="html"
    )
@bot.message_handler(content_types=["text"], func=lambda x: x.chat.id == admin and channels["edited"] != [])
def admin_set_channel(message):
    text = message.text
    if message.json.get("forward_from_chat", False) and message.forward_from_chat.type in ["channel", "group"]:
        ch_id = message.forward_from_chat.id
        print(message)
        try:
            res = bot.create_chat_invite_link(chat_id=ch_id)
        except ApiTelegramException:
            bot.send_message(message.chat.id, "Avval kanalga ushbu botni admin qiling.")
            return
        ch_link = res.invite_link
        text = f"{ch_link}|{ch_id}"
    if message.text.strip()[0] != "@" and not text.startswith("https://t.me/+"):
        bot.send_message(message.chat.id, "Noto'g'ri username qayta kiriting")
        return
    tur, kanal_id = map(str, channels["edited"].pop().split("_"))
    if tur == "a":
        channels["asosiy_kanllar"][f"kanal_{kanal_id}"] = text
    else:
        channels["yuklash_kanal"][f"kanal_{kanal_id}"] = text
    update_channels(channels)
    bot.send_message(message.chat.id, "Kanal muvaffaqiyatli sozlandi 👌")
@bot.message_handler(content_types=["text"], func=lambda x: check_channels(x.chat.id, bot)[0])
def check(message):
    chat_id = message.chat.id
    try:
        num = int(message.text)
        kino = db.get_kino_by_id(kino_id=num)
        if not kino:
            bot.send_message(chat_id=chat_id, text="Ushbu idga mos kino topilmadi")
            return
    except:
        num = -1
    markup = make_markup(check_channels(chat_id, bot)[1])
    markup.add(types.InlineKeyboardButton("Tasdiqlash ✅", callback_data=f"confirm_{num}"))

    bot.send_message(
        chat_id,
        "Kinoni ko'rish uchun quyidagi kanallarga obuna bo'lishingiz kerak\nObuna bo'lib \"Tasdiqlash\" tugmasini bosing.",
        reply_markup=markup
    )
@bot.message_handler(content_types=["video"])
def add_kino(message):
    chat_id = message.chat.id
    if chat_id == admin:
        file_id = message.video.file_id
        name = message.caption
        markup = types.InlineKeyboardMarkup()
        yes = types.InlineKeyboardButton("Yuklash ✅", callback_data="yuklash")
        no = types.InlineKeyboardButton("Bekor qilish ❌", callback_data="cancel")
        markup.row(no, yes)
        bot.send_video(chat_id, file_id, caption=f"🎬 Nomi: {name}\n\n🔒 Kino kodi: ***\n\nBizning Kanal: {channels['glavniy_channel']}", reply_markup=markup)

# Get kino
@bot.message_handler(content_types=["text"])
def text(message):
    try:
        chat_id = message.chat.id
        kino_id = int(message.text)
        # admin uchun tugma
        markup = types.InlineKeyboardMarkup()
        del_b = types.InlineKeyboardButton("O'chirish 🗑", callback_data="delete")
        no = types.InlineKeyboardButton("Yopish ❌", callback_data="close")
        markup.row(no, del_b)
        # user uchun tugma
        markupf = types.InlineKeyboardMarkup()
        yuklab_olish = types.InlineKeyboardButton("📥 Yuklab olish", callback_data=f"yuklash_{kino_id}")
        markupf.add(yuklab_olish)
        # kinoni olish
        kino = db.get_kino_by_id(kino_id=kino_id)
        print(kino)
        if not kino:
            bot.send_message(chat_id=chat_id, text="Ushbu idga mos kino topilmadi")
            return
        if chat_id == admin:
            bot.send_video(chat_id=chat_id, video=kino[2], protect_content=True, caption=f"🎬 Nomi: {kino[1]}\n\n🔒 Kino kodi: {kino[0]}\n\nBizning kanal: {channels['glavniy_channel']}", reply_markup=markup)
        else:
            bot.send_video(chat_id=chat_id, video=kino[2], protect_content=True, caption=f"🎬 Nomi: {kino[1]}\n\n🔒 Kino kodi: {kino[0]}\n\nBizning kanal: {channels['glavniy_channel']}", reply_markup=markupf)
    except:
        bot.send_message(chat_id=chat_id, text="Id xato kiritildi qayta kiriting")

# Query handler
@bot.callback_query_handler(func=lambda x: x.data == "yuklash")
def yuklash(call):
    chat_id = call.message.chat.id
    
    markup = types.InlineKeyboardMarkup()
    del_b = types.InlineKeyboardButton("O'chirish 🗑", callback_data="delete")
    no = types.InlineKeyboardButton("Yopish ❌", callback_data="close")
    markup.row(no, del_b)
    name = call.message.caption[8:][:-len(channels['glavniy_channel'])-35]
    kino_id = db.add_kino(
        name=name,
        file_id=call.message.video.file_id
    )
    bot.edit_message_caption(chat_id=chat_id, message_id=call.message.id, caption=f"🎬 Nomi: {name}\n\n🔒 Kino kodi: {kino_id}\n\nBizning kanal: {channels['glavniy_channel']}", reply_markup=markup)
    print(kino_id)

@bot.callback_query_handler(func=lambda x: x.data.startswith("delete_kanal_"))
def yuklash(call):
    chat_id = call.message.chat.id
    kanal_id = int(call.data.split("_")[-1])
    channels["asosiy_kanllar"][f"kanal_{kanal_id}"] = "-"
    update_channels(channels)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.id, text="Kanal olib tashjlandi ✅")

@bot.callback_query_handler(func=lambda x: x.data.startswith("set_kanal_"))
def set_kanal(call):
    chat_id = call.message.chat.id
    kanal_id = int(call.data.split("_")[-1])
    if f"a_{kanal_id}" not in channels["edited"]:
        channels["edited"].append(f"a_{kanal_id}")
    update_channels(channels)
    # userdan qabul qilish
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Shaxsiy guruh bo'lsa", url=f"https://t.me/{bot_username[1:]}?startgroup=true")) # Add group url
    markup.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data="berok_qilish_kanal_" + str(kanal_id)))

    bot.send_message(chat_id=chat_id, text="Kanal yoki guruh username ni yuboring\n\nMasalan: <code>@kanal_1</code> yoki <code>@guruh_1</code>\n\nShaxsiy kanal bo'lsa biror postini shu yerga forward qiling.", reply_markup=markup, parse_mode="HTML")
@bot.callback_query_handler(func=lambda x: x.data.startswith("berok_qilish_kanal_"))
def bekor_qilish(call):
    chat_id = call.message.chat.id
    kanal_id = int(call.data.split("_")[-1])
    if f"a_{kanal_id}" in channels["edited"]:
        channels["edited"].remove(f"a_{kanal_id}")
    update_channels(channels)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.id, text="Taxrirlash bekor qilindi")

# yuklash uchun ham
@bot.callback_query_handler(func=lambda x: x.data.startswith("delete_ykanal_"))
def yuklash(call):
    chat_id = call.message.chat.id
    kanal_id = int(call.data.split("_")[-1])
    channels["yuklash_kanal"][f"kanal_{kanal_id}"] = "-"
    update_channels(channels)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.id, text="Kanal olib tashjlandi ✅")

@bot.callback_query_handler(func=lambda x: x.data.startswith("set_ykanal_"))
def set_kanal(call):
    chat_id = call.message.chat.id
    kanal_id = int(call.data.split("_")[-1])
    if f"y_{kanal_id}" not in channels["edited"]:
        channels["edited"].append(f"y_{kanal_id}")
    update_channels(channels)
    # userdan qabul qilish
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Shaxsiy guruh bo'lsa", url=f"https://t.me/{bot_username[1:]}?startgroup=true")) # Add group url
    markup.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data="berok_qilish_ykanal_" + str(kanal_id)))

    bot.send_message(chat_id=chat_id, text="Kanal yoki guruh username ni yuboring\n\nMasalan: <code>@kanal_1</code> yoki <code>@guruh_1</code>\n\nShaxsiy kanal bo'lsa biror postini shu yerga forward qiling.", reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda x: x.data.startswith("berok_qilish_ykanal_"))
def bekor_qilish(call):
    chat_id = call.message.chat.id
    kanal_id = int(call.data.split("_")[-1])
    if f"y_{kanal_id}" in channels["edited"]:
        channels["edited"].remove(f"y_{kanal_id}")
    update_channels(channels)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.id, text="Taxrirlash bekor qilindi")



@bot.callback_query_handler(func=lambda x: x.data == "delete")
def yuklash(call):
    chat_id = call.message.chat.id
    kino_id = int(call.message.caption.split("🔒 Kino kodi:")[1][:-len(channels['glavniy_channel'])-16])
    db.delete_kino_by_id(
        kino_id=kino_id
    )
    bot.delete_message(chat_id=chat_id, message_id=call.message.id)
    bot.send_message(chat_id=chat_id, text="Kino o'chirildi ✅")

@bot.callback_query_handler(func=lambda x: x.data in ["close", "cancel"])
def yuklash(call):
    chat_id = call.message.chat.id
    bot.delete_message(chat_id=chat_id, message_id=call.message.id)

@bot.callback_query_handler(func=lambda x: x.data.startswith("yuklash_"))
def yuklash(call):
    if True:
        chat_id = call.message.chat.id
        kino_id = int(call.data.split("_")[-1])
        if check_yuklash(chat_id, bot)[0]:
            markup = make_markup(check_yuklash(call.message.chat.id, bot)[1])
            markup.add(types.InlineKeyboardButton("📥 Qayta yuklash", callback_data=call.data))
            bot.send_message(
                chat_id,
                "Kinoni yuklab olish uchun quyidagi kanallarga obuna bo'lishingiz kerak",
                reply_markup=markup
            )
            return


        # kinoni olish
        kino = db.get_kino_by_id(kino_id=kino_id)
        print(kino)
        if kino:
            bot.send_video(
                chat_id=chat_id,
                video=kino[2],
                caption=f"🎬 Nomi: {kino[1]}\n\n🔒 Kino kodi: {kino[0]}\n\nBizning kanal: {channels['glavniy_channel']}"
            )
    else:
        bot.send_message(chat_id=chat_id, text="Xatolik")

# Tasdiqlash tugmasini bosgan foydalanuvchilar uchun
@bot.callback_query_handler(func=lambda x: x.data.startswith("confirm_"))
def confirm_start(call):
    chat_id = call.message.chat.id
    num = int(call.data.split("_")[-1])
    if check_channels(chat_id, bot)[0]:
        markup = make_markup(check_channels(call.message.chat.id, bot)[1])
        markup.add(types.InlineKeyboardButton("Tasdiqlash ✅", callback_data=f"confirm_{num}"))
        bot.send_message(
            chat_id,
            "Kinoni ko'rish uchun quyidagi kanallarga obuna bo'lishingiz kerak.\n\nObuna bo'lib \"Tasdiqlash\" tugmasini bosing.",
            reply_markup=markup
        )
        return
    try:
        kino = db.get_kino_by_id(kino_id=num)
        markup = types.InlineKeyboardMarkup()
        yuklab_olish = types.InlineKeyboardButton("📥 Yuklab olish", callback_data=f"yuklash_{num}")
        markup.add(yuklab_olish)
        if not kino:
            bot.send_message(chat_id=chat_id, text="Ushbu idga mos kino topilmadi")
            return
        bot.send_video(chat_id=chat_id, video=kino[2], protect_content=True, caption=f"🎬 Nomi: {kino[1]}\n\n🔒 Kino kodi: {kino[0]}\n\nBizning kanal: {channels['glavniy_channel']}", reply_markup=markup)
    except Exception as e:
        bot.send_message(chat_id=chat_id, text="Xatolik qayta urinib ko'ring")
        print(e)

import requests
if True:
    try:
        bot.polling(none_stop=True)
    except requests.exceptions.ConnectTimeout:
        pass

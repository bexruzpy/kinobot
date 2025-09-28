from settings import CHANNELS
from telebot import types
import json

def is_subscribed(user_id, channel, bot):
    if channel == "-":
        return True
    try:
        member = bot.get_chat_member(chat_id=channel, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Xatolik: {e}")
        return False
def check_channels(tg_id, bot):
    not_subcribes = []
    for channel in list(CHANNELS["asosiy_kanllar"].values()): #+[glavniy_channel]:
        if "|" in channel:
            if not is_subscribed(tg_id, channel.split("|")[1], bot):
                not_subcribes.append(channel)
        else:
            if not is_subscribed(tg_id, channel, bot):
                not_subcribes.append(channel)

    return len(not_subcribes) != 0, not_subcribes
def check_yuklash(tg_id, bot):
    not_subcribes = []
    for channel in list(CHANNELS["yuklash_kanal"].values()): #+[glavniy_channel]:
        if not is_subscribed(tg_id, channel, bot):
            not_subcribes.append(channel)
    return len(not_subcribes) != 0, not_subcribes

def make_markup(channels):
    markup = types.InlineKeyboardMarkup()
    n=0
    for channel in channels:
        n+=1
        if channel[0] == "@":
            markup.add(
                types.InlineKeyboardButton(f"Kanal {n}", url=f"https://t.me/{channel[1:]}")
            )
        else:
            markup.add(
                types.InlineKeyboardButton(f"Kanal {n}", url=channel.split("|")[0])
            )
    return markup

# kanallar.json
def update_channels(data):
    for key, channel  in data["asosiy_kanllar"].items():
        data["asosiy_kanllar"][key] = channel #.get_save()
    for key, channel  in data["yuklash_kanal"].items():
        data["yuklash_kanal"][key] = channel #.get_save()
    with open("kanallar.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

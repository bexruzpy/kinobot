import json

bot_token = "7559742423:AAHFxTlvZ97kqVgFfAnAtRT_4ivszotPa_0"

bot_username = "@kino_premium_uzbot"


def get_channels():
    with open("kanallar.json", "r", encoding="utf-8") as f:
        return json.load(f)
class Chanel:
    def __init__(self, string):
        if string[0] == "@":
            self.id = string
            self.url = f"https://t.me/{string[1:]}"
        else:
            self.id = string.split("|")[0]
            self.url = string.split("|")[1]
    def get_save(self):
        return f"{self.id}|{self.url}"
    def __str__(self):
        return f"{self.id}"
    def __repr__(self):
        return f"{self.id}"

channels = get_channels()



admin = 6214332023
# admin = 5139310978


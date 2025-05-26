from types import NoneType
from pyrogram.methods.decorators import on_message
from pyrogram import Client, filters
from pyrogram.types import WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv
import requests
import pprint
import re
import os


load_dotenv()

URL = os.getenv('url')
API_ID = os.getenv('api_id') 
API_HASH = os.getenv('api_hash')
BOT_TOKEN = os.getenv('bot_token')
bot_client = Client('my_bot', API_ID, API_HASH, bot_token=BOT_TOKEN)



@bot_client.on_message(filters.text)
def handler(client, message):
    
    #user_id = str(message.from_user.id)
    res_url = re.search(r'\bhttps://music.yandex.ru/\S+', message.text) # https://music.yandex.ru/users/music-blog/playlists/2106?utm_source=web&utm_medium=copy_link
    if message.text == "/start":
        print("STARTED")
        bot_client.send_message(message.chat.id, text="Пришли мне ссылку на альбом / плейлист / трек  от яндекс.музыки")
        return None
    elif not res_url or res_url == NoneType or (res_url.group()[:30:] != "https://music.yandex.ru/album/" and res_url.group()[:30:] != "https://music.yandex.ru/users/"):
        bot_client.send_message(message.from_user.id, "не обнаружена ссылка / неподдерживаемый формат", reply_to_message_id=message.id)
        print(message.text)
        return None
    try:
        with requests.session() as client:
            client.get(URL)
            if 'csrftoken' in client.cookies:
                csrftoken = client.cookies['csrftoken']
                print(message.text)
                try:
                    x = client.post(URL, data={"csrfmiddlewaretoken": csrftoken, "idf":message.text}, timeout=10)
                    if x.status_code == 200:
                        button = KeyboardButton(text="плеер", web_app=WebAppInfo(url="https://quevolt.github.io/"))
                        reply = ReplyKeyboardMarkup([[button]], is_persistent=False, one_time_keyboard=True, resize_keyboard=True, selective=True)
                        bot_client.send_message(message.chat.id, text="Готово! Теперь вы можете приступить к прослушиванию", reply_markup=reply, reply_to_message_id=message.id)
                except requests.exceptions.ConnectionError as e:
                    x = "No response"
                    bot_client.send_message(message.chat.id, text="Сервер не отвечает", reply_to_message_id=message.id)
                except requests.exceptions.ReadTimeout:
                    x = "Read timed out"
                print(x)
    except requests.exceptions.ConnectionError as e:
        print("ошибка на стороне сервера")
        print(e)
        bot_client.send_message(message.chat.id, text="Проблема с подключением к серверу", reply_to_message_id=message.id)
bot_client.run()


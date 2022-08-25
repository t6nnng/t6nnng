import telebot
import json
from telebot import types
import time
import threading

with open("settings.json", 'r', encoding="utf-8") as f:
    data = json.loads(f.read())
    
owner=int(data["owner_id"])
chat=data["chat_id"]
token=data["token"]

b = 0

bot = telebot.TeleBot(token)

kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
add=types.KeyboardButton("Добавить сообщение")
List=types.KeyboardButton("Список сообщений")
kb.add(add)
kb.add(List)

def check(): 
    while True:
        now=time.ctime().split()[3].split(':')
        with open('settings.json', 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
            for m in data["messages"]:
                for tm in m[1].split(','):
                    if tm.split('.')[0] == str(now[0]) and tm.split('.')[1] == str(now[1]) and m[2] == 1:
                        bot.send_message(chat, m[0])
        time.sleep(60)
        
        
t1 = threading.Thread(target=check)
t1.start()

@bot.message_handler(commands=['start'], func=lambda m: m.from_user.id == owner)
def start(m):
    bot.send_message(m.from_user.id, f"Здраствуйте, {m.from_user.first_name}!", reply_markup=kb)
    
@bot.message_handler(content_types=['text'], func=lambda m: m.from_user.id == owner)
def message(m):
    if m.text == "Список сообщений":
        with open('settings.json', 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
            mess = "Список сообщений:\n\n"
            kb1 = types.InlineKeyboardMarkup()
            for me in data['messages']:
                mess += f'Текст сообщения: "{me[0]}", время отправления: {me[1]}, {me[2] == 1}\n\n'
                kb1.add(types.InlineKeyboardButton(text=f"Действия с сообщением {data['messages'].index(me)}", callback_data=f"adv_{data['messages'].index(me)}"))
            bot.send_message(m.from_user.id, mess, reply_markup=kb1)
    elif m.text == "Добавить сообщение":
        a = bot.send_message(m.from_user.id, "Хорошо, отправьте текст сообщения и время отправки(в формате ЧЧ.ММ) разделяя их _(пример: пример сообщения_13.05")
        bot.register_next_step_handler(a, name)
        
def name(m):
    text = m.text.split('_')
    with open('settings.json', 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
        data['messages'].append([text[0], text[1], 1])
        with open('settings.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            bot.send_message(m.from_user.id, f"Сообщениие будет отправлено в {text[1]}")
            
@bot.callback_query_handler(func=lambda call: True)
def inline_callback(call):
    global b
    text = call.data.split('_')
    if "adv" in text:
        kb2 = types.InlineKeyboardMarkup()
        kb2.add(types.InlineKeyboardButton(text="Изменить время отправки", callback_data=f"change_{text[1]}"))
        kb2.add(types.InlineKeyboardButton(text="Изменить активность сообщения", callback_data=f"onoff_{text[1]}"))
        kb2.add(types.InlineKeyboardButton(text="Удалить сообщение", callback_data=f"delete_{text[1]}")),
        bot.send_message(call.from_user.id, "Выберите действие:", reply_markup=kb2)
    elif "change" in text:
        a = bot.send_message(call.from_user.id, "Введите новое время отправки:")
        b= int(text[1])
        bot.register_next_step_handler(a, new_time)
    elif "onoff" in text:
        with open('settings.json', 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
            if data['messages'][int(text[1])][2] == 0:
                data['messages'][int(text[1])][2] = 1
                bot.send_message(call.from_user.id, "Сообщение активировалось!")
            else:
                data['messages'][int(text[1])][2] = 0
                bot.send_message(call.from_user.id, "Сообщение отключилось!!")
                with open('settings.json', 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
    elif "delete" in text:
        with open('settings.json', 'r', encoding='utf-8') as f:
             data =  json.loads(f.read())
             del(data['messages'][text[1]])
             bot.send_message(call.from_user.id, "Сообщение удалено")
             with open('settings.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
                
            
        
def new_time(m):
    global b
    with open('settings.json', 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
        data['messages'][b][1] = m.text
        with open('settings.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            bot.send_message(m.from_user.id, f"Сообщениие будет отправлено в {m.text}")
    
bot.polling(none_stop=True)
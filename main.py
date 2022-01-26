import gspread
import telebot
import json
from telebot import types

token = "5161683680:AAFdI8X7ETiekHdvLoRFjuXU6VyWUd6Vwhk"

bot = telebot.TeleBot(token)

gc = gspread.service_account("service_account.json")
sh = gc.open_by_key("1oMGsisgYxW-6_m9xawhOgqPz3QxaCR23X_yYQRnoRyo")
sheet = sh.get_worksheet(0)
header = False
category_sheet = sh.get_worksheet(1)
CATEGORY_LAST_UPDATED_TIME = None
options = None
POSTS_CACHE = {}

def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)


def draw_keyboard(options, chat_id):
    markup = types.InlineKeyboardMarkup()
    cmds = [types.InlineKeyboardButton(text=f"{i}", callback_data=f"{i};;{chat_id}") for i in options]
    index = 0

    while index < len(cmds):
        try:
            markup.row(cmds[index], cmds[index+1], cmds[index+2])

        except IndexError:
            try:
                markup.row(cmds[index], cmds[index+1])

            except IndexError:
                markup.row(cmds[index])

        index += 3

    return markup



@bot.message_handler(func=lambda message: True, content_types=['video','text','photo','animation', "sticker"])
def handle_post(message):
    options = category_sheet.get_all_values()
    options = [item for sublist in options for item in sublist] # to make flat list
    bot.send_message(message.chat.id, "Choose a category:", reply_markup=draw_keyboard(options, message.from_user.id))


@bot.callback_query_handler(func=lambda call: True)
def callback_hander(call):
    global header

    if call.data:
        user_id = call.from_user.id
        username = call.from_user.username
        first_name = call.from_user.first_name
        group_id = call.message.json["chat"]["id"]
        split_data = call.data.split(';;')
        catagorey = split_data[0]

        if POSTS_CACHE.get(call.message.id):
            bot.send_message(call.message.chat.id, POSTS_CACHE.get(call.message.id))

        if user_id != int(split_data[1]) or POSTS_CACHE.get(call.message.id): return

        if not header:
            sheet.update('A1:E1', [["user_id", "username", "first_name", "group_id", "category"]])
            sheet.format('A1:F1', {"textFormat": {"bold": True}, "horizontalAlignment": "CENTER"})
            header = True
        next_row = next_available_row(sheet)
        sheet.update(f"A{next_row}:E{next_row}", [[user_id, username, first_name, group_id, catagorey]])
        print("worksheet updated.")
        bot.send_message(call.message.chat.id,f"Post submitted successfully for {catagorey}")
        POSTS_CACHE[call.message.id]=f"Post already submitted for {catagorey}"


print(bot.get_me())
bot.infinity_polling()

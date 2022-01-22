import gspread
import telebot
import json
from telebot import types


def get_config():
    with open("config.json", "r") as f:
        return json.loads(f.read())


config = get_config()
token = config["token"]

bot = telebot.TeleBot(token)

gc = gspread.service_account()
sh = gc.open_by_key("1yMsfNza-JlYPx20kQWNHuqH882Rq56bNJL2rnQO8xBM")
sheet = sh.get_worksheet(0)
header = False

catagory_options = "A B C D E F G H I".split()

def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)


def draw_keyboard(options):
    markup = types.InlineKeyboardMarkup()
    cmds = [types.InlineKeyboardButton(text=f"{i}", callback_data=f"{i}") for i in options]
    index = 0

    while index < len(cmds):
        try:
            markup.row(cmds[index], cmds[index+1], cmds[index+2])

        except IndexError:
            markup.row(cmds[index])

        index += 3

    return markup


# @bot.message_handler(content_types=["text", "photo"])
# @bot.channel_post_handler(func=lambda message:True,content_types=['video','text','photo','animation', "sticker"])

@bot.message_handler(func=lambda message: True, content_types=['video','text','photo','animation', "sticker"])
def handle_post(message):
    bot.send_message(message.chat.id, "Choose a category:", reply_markup=draw_keyboard(catagory_options))

    # bot.edit_message_reply_markup(message.chat.id, message.id, reply_markup=draw_keyboard(catagory_options))



@bot.callback_query_handler(func=lambda call: True)
def callback_hander(call):
    global header
    
    if call.data:
        user_id = call.from_user.id
        username = call.from_user.username
        first_name = call.from_user.first_name
        group_id = call.message.json["chat"]["id"]
        catagorey = call.data
        if not header:
            sheet.update('A1:E1', [["user_id", "username", "first_name", "group_id", "category"]])
            sheet.format('A1:F1', {"textFormat": {"bold": True}, "horizontalAlignment": "CENTER"})
            header = True
        next_row = next_available_row(sheet)
        sheet.update(f"A{next_row}:E{next_row}", [[user_id, username, first_name, group_id, catagorey]])
        print("worksheet updated.")


print(bot.get_me())
bot.infinity_polling()
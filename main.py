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
sh = gc.open_by_key("1oMGsisgYxW-6_m9xawhOgqPz3QxaCR23X_yYQRnoRyo")
sheet = sh.get_worksheet(0)
header = False
category_sheet = sh.get_worksheet(1)
CATEGORY_LAST_UPDATED_TIME = None
# options = catagorey_sheet.get_all_values()
# options = [item for sublist in options for item in sublist] # to make flat list

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
            try:
                markup.row(cmds[index], cmds[index+1])

            except IndexError:
                markup.row(cmds[index])

        index += 3

    return markup



@bot.message_handler(func=lambda message: True, content_types=['video','text','photo','animation', "sticker"])
def handle_post(message):
    global CATEGORY_LAST_UPDATED_TIME
    is_updated = False

    if CATEGORY_LAST_UPDATED_TIME is None:
        CATEGORY_LAST_UPDATED_TIME = category_sheet.lastUpdateTime
        is_updated = True

    elif CATEGORY_LAST_UPDATED_TIME  != category_sheet.lastUpdateTime:
        CATEGORY_LAST_UPDATED_TIME = category_sheet.lastUpdateTime  
        is_updated = True

    if is_updated:
        options = category_sheet.get_all_values()
        options = [item for sublist in options for item in sublist] # to make flat list
       
    
        bot.send_message(message.chat.id, "Choose a category:", reply_markup=draw_keyboard(options))


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
from aiogram import types
import os
from dotenv import load_dotenv

load_dotenv()

def is_bot_name_consists(message: types.Message):
    s = " " + message.text.lower() + " "
    for name in os.getenv("BOT_NAME"):
        lst = s.split(name)
        if len(lst) > 1:
            return True
    return False
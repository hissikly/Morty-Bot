from aiogram import types
import os
from dotenv import load_dotenv

def is_bot_name_consists(message: types.Message):
    s = message.text.lower()
    bot_name = ["морти", "morty", "морт"]
    for name in bot_name:
        if name in s:
            return True
    return False
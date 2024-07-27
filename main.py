from aiogram import Bot, Dispatcher, types
import chat_model
import sup_functions
import asyncio
from aiogram.enums import ParseMode
import os
from dotenv import load_dotenv
from aiogram.filters.command import Command
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext


load_dotenv()

bot = Bot(os.getenv("BOT_TOKEN"))
dp = Dispatcher()


class ImageRate(StatesGroup):
    image_rate = State()


@dp.message(StateFilter(None), Command("image"))
async def get_image_command(mes: types.Message, state: FSMContext):
    await mes.answer("Опишите то, что вы хотите увидеть на картинке")

    await state.set_state(ImageRate.image_rate)


@dp.message(ImageRate.image_rate)
async def get_image_rate(mes: types.Message, state: FSMContext):
    await mes.answer("Запускаю генерацию изображения...")

    answer_title = await chat_model.get_image_by_gigachat(mes)
    await mes.answer_photo(photo=FSInputFile("image/img.jpg", "image"), caption=answer_title)
    await state.clear()


@dp.message()
async def get_random_mes(mes: types.Message):
    if mes.chat.type == "private":
        bot_answer = await chat_model.get_message_by_gigachain(mes)
        await mes.answer(bot_answer, parse_mode=ParseMode.MARKDOWN)
    else:
        if sup_functions.is_bot_name_consists(mes):
            bot_answer = await chat_model.get_message_by_gigachain(mes)
            await mes.answer(bot_answer, parse_mode=ParseMode.MARKDOWN)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
# from typing import List, Any

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from db_handler import DBHandler
from stats import Statistics
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import fsm
from keyboard_helper import Keyboard


bot = Bot("5912650315:AAGIEvhvN0YKLASCKL4rKZg56DuZ_UlgIAc")
dp = Dispatcher(bot, storage=MemoryStorage())
fsm.register_handlers_films(dp)


@dp.message_handler(commands="start")
async def send_welcome(message: types.Message):
    keyboard = Keyboard(["Поиск", "Помощь", "Статистика", "История"]).keyboard
    await message.reply("Привет! 👋\nЯ - cinemabot, помогу тебе подобрать фильм 🍿"
                        "\nЖми 'Поиск'!", reply_markup=keyboard)


@dp.message_handler(commands="help")
@dp.message_handler(Text(equals="Помощь", ignore_case=True))
async def help(message: types.Message):
    keyboard = Keyboard(["Поиск", "Помощь", "Статистика", "История"]).keyboard
    await message.reply("Напиши 'Поиск' и я подберу тебе фильм!\n"
                        "Если интересует история поиска, то жми 'История'\n"
                        "Если хочешь посмотреть статистику, "
                        "то жми 'Статистика'\n"
                        "Если хочешь узнать, что я умею, то жми 'Помощь'",
                        reply_markup=keyboard)


# todo fix output
@dp.message_handler(commands="stats")
@dp.message_handler(Text(equals="Статистика", ignore_case=True))
async def stats(message: types.Message):
    keyboard = Keyboard(["Поиск", "Помощь", "Статистика", "История"]).keyboard
    database = await DBHandler.create(
        'postgres', 'cine123bot',
        '5.188.142.77', '5435',
        'postgres')

    statistic = Statistics(database)
    res2 = await statistic.get_films_count_for_user(message.from_user.id)
    res2 = [(i[0], i[1]) for i in res2]
    stat = "\n".join([f"{i[0]}: {i[1]}" for i in res2])
    await message.answer(f"<b>Твоя статистика поиска</b> 🎦:\n{stat}",
                         reply_markup=keyboard,
                         parse_mode="HTML")


# todo fix output
@dp.message_handler(commands="history")
@dp.message_handler(Text(equals="История", ignore_case=True))
async def history(message: types.Message):
    keyboard = Keyboard(["Поиск", "Помощь", "Статистика", "История"]).keyboard
    database = await DBHandler.create(
        'postgres', 'cine123bot',
        '5.188.142.77', '5435',
        'postgres')
    statistic = Statistics(database)
    res = await statistic.get_history_for_user(message.from_user.id)
    res = [i[0] for i in res]
    await message.answer(f"<b>Твоя история поиска</b> ⏳: {', '.join(res)}",
                         reply_markup=keyboard,
                         parse_mode="HTML")


if __name__ == '__main__':
    executor.start_polling(dp)

from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from db_handler import DBHandler
from film_info_parser import IMDBSearcher


class ChooseFilm(StatesGroup):
    waiting_for_film_title = State()


async def films_start(message: types.Message, state: FSMContext):
    await message.answer("Введи название фильма",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ChooseFilm.waiting_for_film_title.state)


async def film_chosen(message: types.Message, state: FSMContext):
    await state.update_data(chosen_title=message.text.lower())
    searcher = IMDBSearcher('http://www.omdbapi.com/', 'f9f6197c')
    database = await DBHandler.create(
        'postgres', 'cine123bot',
        '5.188.142.77', '5435',
        'postgres')
    user_data = await state.get_data()
    info = await searcher.get_film_info_by_title(user_data['chosen_title'])

    await message.answer_photo(info['Poster'],
                               caption=f"Название: {info['Title']}\n"
                                       f"Год: {info['Year']}\n"
                                       f"Режиссер: {info['Director']}\n"
                                       f"Актеры: {info['Actors']}\n"
                                       f"Описание: {info['Plot']}\n")
    await database.execute_query_without_return(
        f"INSERT INTO stats (telegram_user_id, telegram_username,"
        f" search_query, response) "
        f"VALUES ({message.from_user.id}, '{message.from_user.username}', "
        f"'{message.text}', '{info['Title']}');")

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Поиск", "Помощь", "Статистика", "История"]
    keyboard.add(*buttons)
    await message.answer("Что дальше?", reply_markup=keyboard)

    await state.finish()


def register_handlers_films(dp: Dispatcher):
    dp.register_message_handler(films_start, Text(equals="Поиск"), state="*")
    dp.register_message_handler(film_chosen,
                                state=ChooseFilm.waiting_for_film_title)

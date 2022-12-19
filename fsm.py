from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from credentials import (CX, DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER,
                         GOOGLE_API_KEY, KINOPOISK_API_KEY)
from db_handler import DBHandler
from film_info_parser import KinopoiskSearcher
from google_searcher import get_link
from keyboard_helper import Keyboard

KINOPOISK_URL = "https://kinopoiskapiunofficial.tech/api/v2.1/"


class ChooseFilm(StatesGroup):
    waiting_for_film_title = State()


async def films_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Введи название фильма", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(ChooseFilm.waiting_for_film_title.state)


async def film_chosen(message: types.Message, state: FSMContext):
    await state.update_data(chosen_title=message.text.lower())
    searcher = KinopoiskSearcher(KINOPOISK_URL, KINOPOISK_API_KEY)
    database = await DBHandler.create(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
    user_data = await state.get_data()
    info = await searcher.get_film_info_by_title(user_data["chosen_title"])
    keyboard = Keyboard(["Поиск", "Помощь", "Статистика", "История"]).keyboard
    if not info["films"]:
        await message.answer("Фильм не найден")
        await message.answer("Что дальше?", reply_markup=keyboard)
        await state.finish()
        return
    # await message.answer_photo()
    if "nameEn" not in info["films"][0]:
        title = info["films"][0]["nameRu"]
    else:
        title = f"{info['films'][0]['nameRu']} ({info['films'][0]['nameEn']})"

    watching_link = await get_link(
        f"{info['films'][0]['nameRu']} смотреть онлайн бесплатно",
        GOOGLE_API_KEY,
        CX
    )

    await message.answer_photo(
        info["films"][0]["posterUrl"],
        caption=f"<b>Название</b>: {title}\n"
        f"<b>Год</b>: "
        f"{info['films'][0]['year']}\n"
        f"<b>Жанр</b>: "
        f"{', '.join([genre['genre'] for genre in info['films'][0]['genres']])}\n"
        f"<b>Продолжительность</b>: "
        f"{info['films'][0]['filmLength']}\n"
        f"<b>Описание</b>: "
        f"{info['films'][0]['description']}\n"
        f"<b>Рейтинг</b>: "
        f"{info['films'][0]['rating']}\n"
        f"<a href='{watching_link}'>Смотреть</a>",
        parse_mode="HTML",
    )
    await database.execute_query_without_return(
        f"INSERT INTO stats (telegram_user_id, telegram_username,"
        f" search_query, response) "
        f"VALUES ({message.from_user.id}, '{message.from_user.username}', "
        f"'{message.text}', '{info['films'][0]['nameRu']}');"
    )

    await message.answer("Что дальше?", reply_markup=keyboard)
    await state.finish()


def register_handlers_films(dp: Dispatcher):
    dp.register_message_handler(films_start, Text(equals="Поиск"), state="*")
    dp.register_message_handler(film_chosen, state=ChooseFilm.waiting_for_film_title)

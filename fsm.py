from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.deep_linking import get_start_link
import aiogram.utils.markdown as fmt

from db_handler import DBHandler
from film_info_parser import IMDBSearcher, KinopoiskSeracher
from keyboard_helper import Keyboard
from yandex_searcher import get_yandex_search_links
from google_searcher import get_links


class ChooseFilm(StatesGroup):
    waiting_for_film_title = State()


async def films_start(message: types.Message, state: FSMContext):
    await message.answer("Введи название фильма",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ChooseFilm.waiting_for_film_title.state)


async def film_chosen(message: types.Message, state: FSMContext):
    await state.update_data(chosen_title=message.text.lower())
    # searcher = IMDBSearcher('http://www.omdbapi.com/', 'f9f6197c')
    searcher = KinopoiskSeracher(
        "https://kinopoiskapiunofficial.tech/api/v2.1/",
        "567aad23-ba6e-4412-9461-f96808488730"
    )
    database = await DBHandler.create(
        'postgres', 'cine123bot',
        '5.188.142.77', '5435',
        'postgres')
    user_data = await state.get_data()
    info = await searcher.get_film_info_by_title(user_data['chosen_title'])
    keyboard = Keyboard(
        ["Поиск", "Помощь", "Статистика", "История"]).keyboard
    if not info['films']:
        await message.answer("Фильм не найден")
        await message.answer("Что дальше?", reply_markup=keyboard)
        await state.finish()
        return
    # await message.answer_photo()
    if 'nameEn' not in info['films'][0]:
        title = info['films'][0]['nameRu']
    else:
        title = f"{info['films'][0]['nameRu']} ({info['films'][0]['nameEn']})"

    watching_link = await get_links(
        f"{info['films'][0]['nameRu']} смотреть онлайн бесплатно", 1)

    await message.answer_photo(info['films'][0]['posterUrl'],
                               caption=f"<b>Название</b>: {title}\n"
                                       f"<b>Год</b>: {info['films'][0]['year']}\n"
                                       f"<b>Жанр</b>: {', '.join([genre['genre'] for genre in info['films'][0]['genres']])}\n"
                                       f"<b>Продолжительность</b>: {info['films'][0]['filmLength']}\n"
                                       f"<b>Описание</b>: {info['films'][0]['description']}\n"
                                       f"<b>Рейтинг</b>: {info['films'][0]['rating']}\n"
                                       f"<a href='{watching_link[0]}'>Смотреть</a>",
                               parse_mode="HTML")
    await database.execute_query_without_return(
        f"INSERT INTO stats (telegram_user_id, telegram_username,"
        f" search_query, response) "
        f"VALUES ({message.from_user.id}, '{message.from_user.username}', "
        f"'{message.text}', '{info['films'][0]['nameRu']}');")

    await message.answer("Что дальше?", reply_markup=keyboard)
    await state.finish()


def register_handlers_films(dp: Dispatcher):
    dp.register_message_handler(films_start, Text(equals="Поиск"), state="*")
    dp.register_message_handler(film_chosen,
                                state=ChooseFilm.waiting_for_film_title)

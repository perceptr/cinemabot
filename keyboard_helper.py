from aiogram import types


class Keyboard:
    def __init__(self, buttons: list):
        self.keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.__buttons = buttons
        self.keyboard.add(*self.__buttons)

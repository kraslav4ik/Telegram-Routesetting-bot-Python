import datetime
import unittest
from queue import Queue
from unittest.mock import Mock

from telegram import Update, Chat, User, Message, InlineKeyboardMarkup, InlineKeyboardButton, Bot
from telegram.ext import CallbackContext, Dispatcher, ExtBot

from src.Menu import Menu


class TestMenu(unittest.TestCase):

    def setUp(self) -> None:
        self.menu = Menu(table_path='data\\Routesetting-Test.xlsx')
        self.token = ''  # bot_token
        self.bot_id = 0  # bot_id
        self.update_id = 0  # update_id
        self.chat_id = 0  # chat_id
        self.first_user_id = 0  # first_test_user_id
        self.second_user_id = 0  # second_test_user_id
        self.chat = Chat(self.chat_id, type='group')
        self.first_user = User(self.first_user_id, first_name='test_user_1', is_bot=False, username='test_user_1')
        self.bot = Bot(self.token)
        self.ext_bot = ExtBot(self.token)
        self.dispatcher = Dispatcher(self.bot, Queue())
        self.message = Message(message_id=1442, text='/menu', date=datetime.datetime.today(),
                               chat=self.chat, from_user=self.first_user, bot=self.bot)
        self.context = CallbackContext(dispatcher=self.dispatcher)
        self.update = Update(update_id=self.update_id, message=self.message)

    def test_setter_menu(self):
        keyboard = [[InlineKeyboardButton('Таблица накрутки', callback_data='1')],
                    [InlineKeyboardButton('Сколько я накрутил', callback_data='2')],
                    [InlineKeyboardButton('Кто в этом месяце накрутил больше всех', callback_data='3')],
                    [InlineKeyboardButton('Внести свои результаты', callback_data='4')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.update.message = Mock()
        self.assertEqual(self.menu.setter_menu(self.update, self.context), self.menu.START)
        self.update.message.reply_text.assert_called_with('Please choose:', reply_markup=reply_markup)


if __name__ == '__main__':
    unittest.main()

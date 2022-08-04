import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from Storage import Storage, AddSetterStatus


class Menu(object):

    def __init__(self, storage: Storage = None, logger=None):
        self.storage = storage or Storage()
        self.logger = logger or logging.getLogger()
        self.ADMIN_START, self.AWAIT_SETTER_USERNAME = range(2)
        self.START, self.AWAIT_RESULT = range(2)

    def user_menu(self, update: Update, context: CallbackContext) -> None:
        message = update.effective_message.text
        user = update.effective_user.username.strip().lower()
        self.logger.info(f'{user} wrote the command "{message}"')
        keyboard = [[InlineKeyboardButton('Мои результаты за месяц', callback_data='show_results')],
                    [InlineKeyboardButton('Кто в этом месяце накрутил больше всех', callback_data='richest')],
                    [InlineKeyboardButton('Внести свои результаты', callback_data='add_results')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please choose:', reply_markup=reply_markup)
        self.logger.info('Bot offered a menu')
        return self.START

    def admin_menu(self, update: Update, context: CallbackContext):
        # if not is_admin_message(update, context):
        #     update.message.reply_text(f'Ты не Босс. Только он может написать {update.effective_message.text}')
        #     return
        keyboard = [[InlineKeyboardButton('Закончить текущий месяц', callback_data='end_period')],
                    [InlineKeyboardButton('Изменить накрутку на неделе', callback_data='change')],
                    [InlineKeyboardButton('Добавить рутсеттера', callback_data='add_setter')],
                    [InlineKeyboardButton('Удалить рутсеттера', callback_data='remove_setter')],
                    # [InlineKeyboardButton('Добавить контест', callback_data='add_contest')],
                    # [InlineKeyboardButton('Удалить контест', callback_data='remove_contest')],
                    # [InlineKeyboardButton('Изменить накрутку на следующей(или уже этой) неделе', callback_data='change')]
                    ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please choose:', reply_markup=reply_markup)
        self.logger.info('Bot offered an admin_menu')
        return self.ADMIN_START

    def add_setter_button(self, update: Update, context: CallbackContext):
        return

    def remove_setter_button(self, update: Update, context: CallbackContext):
        return


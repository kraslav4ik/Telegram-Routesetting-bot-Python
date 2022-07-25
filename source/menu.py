import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from Storage import Storage, AddSetterStatus


class Menu(object):

    def __init__(self, storage: Storage = None, logger=None):
        self.storage = storage or Storage()
        self.logger = logger or logging.getLogger()
        self.ADMIN_START, self.AWAIT_SETTER_USERNAME = range(2)

    # def admin_menu(self, update: Update, context: CallbackContext):
    #     # if not is_admin_message(update, context):
    #     #     update.message.reply_text(f'Ты не Босс. Только он может написать {update.effective_message.text}')
    #     #     return
    #     keyboard = [[InlineKeyboardButton('Добавить рутсеттера', callback_data='add_setter')],
    #                 [InlineKeyboardButton('Удалить рутсеттера', callback_data='remove_setter')],
    #                 # [InlineKeyboardButton('Добавить контест', callback_data='add_contest')],
    #                 # [InlineKeyboardButton('Удалить последний добавленный контест', callback_data='remove_contest')],
    #                 # [InlineKeyboardButton('Изменить накрутку на следующей(или уже этой) неделе', callback_data='change')]
    #                 ]
    #     reply_markup = InlineKeyboardMarkup(keyboard)
    #     update.message.reply_text('Please choose:', reply_markup=reply_markup)
    #     self.logger.info('Bot offered an admin_menu')
    #     return self.ADMIN_START
    #
    # def add_setter(self, update: Update, context: CallbackContext):
    #     chat_id = update.effective_chat.id
    #     query = update.callback_query
    #     user = query.from_user.username.strip().lower()
    #     query.edit_message_text(text=f"Выбранный вариант: {query.data}.")
    #     self.logger.info(f'{user} has selected "{query.data}"')
    #     context.bot.send_message(chat_id,
    #                              text='Введите ник рутсеттера которого нужно добавить: @сеттер')
    #     return self.AWAIT_SETTER_USERNAME
    #
    # def choose_setter(self, update: Update, context: CallbackContext):
    #     chat_id = update.effective_chat.id
    #     setter_name = update.effective_message.text.strip().lower()
    #     self.logger.info(f'Owner want to add setter: "{setter_name}"')
    #     status = self.storage.add_setter().value
    #     if status == AddSetterStatus.ADDED.value:
    #         context.bot.send_message(chat_id, f'Сеттер {setter_name} успешно добавлен')
    #         return
    #     if status == AddSetterStatus.ALREADY_EXISTS.value:
    #         context.bot.send_message(chat_id, f'Сеттер {setter_name} уже есть в таблице')
    #         return
    #     if status == AddSetterStatus.TABLE_ERROR:
    #         context.bot.send_message(chat_id, f'ERROR while adding setter')



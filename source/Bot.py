import logging
from telegram.ext import CallbackContext, ConversationHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from Storage import Storage
from setting_process import SettingProcess


class RoutesettingBot(object):

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.description = "Hey"
        self.storage = Storage()
        self.setting_process = SettingProcess(self.storage)
        self.START = 1
        self.ADMIN_START = 1

    def user_menu(self, update: Update, context: CallbackContext) -> int:
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

    def admin_menu(self, update: Update, context: CallbackContext) -> int:
        # if not is_admin_message(update, context):
        #     update.message.reply_text(f'Ты не Босс. Только он может написать {update.effective_message.text}')
        #     return
        keyboard = [[InlineKeyboardButton('Закончить текущий месяц', callback_data='end_period')],
                    [InlineKeyboardButton('Изменить накрутку на неделе', callback_data='change')],
                    [InlineKeyboardButton('Добавить рутсеттера', callback_data='add_setter')],
                    [InlineKeyboardButton('Удалить рутсеттера', callback_data='remove_setter')],
                    ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please choose:', reply_markup=reply_markup)
        self.logger.info('Bot offered an admin_menu')
        return self.ADMIN_START

    def stop(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        self.logger.info("User %s canceled the conversation.", user.username)
        return ConversationHandler.END

    def unknown(self, update: Update, context: CallbackContext) -> None:
        message = update.effective_message.text
        user = update.effective_user.username.strip().lower()
        self.logger.info(f'{user} wrote the unknown command "{message}"')
        context.bot.send_message(chat_id=update.effective_chat.id, text="Я не знаю такой команды.")
        self.logger.info('bot answered to the unknown command')

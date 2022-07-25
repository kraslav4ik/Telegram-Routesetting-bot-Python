import logging
from telegram.ext import CallbackContext, ConversationHandler
from telegram import Update
from Storage import Storage
from setting_process import SettingProcess
from menu import Menu


class RoutesettingBot(object):

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.description = "Hey"
        self.storage = Storage()
        self.setting_process = SettingProcess(self.storage)
        self.menu = Menu(self.storage)

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

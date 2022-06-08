import logging
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from Scheduler import Scheduler
from Menu import Menu
from utils import get_button_tap_info, is_admin_choice, is_setters_chat


class RoutesettingBot:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.scheduler = Scheduler()
        self.menu = Menu()
        self.description = """
Привет. Я бот ведущий статистику накрутки.
Вот что я умею на данный момент:
1. Все ведение таблицы (т.е. занесение результатов, подсчеты и тд) осуществляю я
2. В конце каждого месяца я присылаю вам ваши результаты для того чтобы свериться
3. В конце каждой недели я узнаю у создателя этой беседы, когда мы крутим на следующей неделе и создам опрос чтобы узнать, кто будет крутить
4. В выбранные им дни я сам пришлю вам опрос о результатах накрутки
Я знаю следующие команды:
    /menu - пользовательское меню, где можно:
        - Посмотреть таблицу накрутки
        - Узнать свои результаты за текущий месяц
        - Узнать кто накрутил больше всех
        - Поправить свои результаты (всякое случается, результаты всегда можно занести вручную, с помощью этой функции)
    /admin_menu - меню босса
    /help или /start - команды для просмотра информации (если вдруг вы забыли что я умею)
Удачи!
                            """

    @is_setters_chat
    def start(self, update: Update, context: CallbackContext) -> None:
        user = update.effective_user.username.strip().lower()
        self.logger.info(f'{user} wrote the "/start" or "/help" command')
        context.bot.send_message(chat_id=update.effective_chat.id, text=self.description)
        self.logger.info('bot answered to the "/start" command')
        return

    def unknown(self, update: Update, context: CallbackContext) -> None:
        message = update.effective_message.text
        user = update.effective_user.username.strip().lower()
        self.logger.info(f'{user} wrote the unknown command "{message}"')
        context.bot.send_message(chat_id=update.effective_chat.id, text="Я не знаю такой команды.")
        self.logger.info('bot answered to the unknown command')

    @is_setters_chat
    def stop(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        self.logger.info("User %s canceled the conversation.", user.username)
        return ConversationHandler.END

    def change_button(self, update: Update, context: CallbackContext):
        info = get_button_tap_info(update)
        if is_admin_choice(context, info):
            self.menu.menu_option(update, context)
            self.scheduler.new_week(context)
            return ConversationHandler.END
        return self.menu.ADMIN_START

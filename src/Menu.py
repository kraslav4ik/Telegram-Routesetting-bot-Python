import logging
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from TableTools import RoutesetterTable, SetterStatus, ContestStatus, ResultStatus
from utils import is_admin_choice, is_admin_message, get_button_tap_info, is_setters_chat


class Menu:

    def __init__(self, table_path=None, logger=None):
        if not table_path:
            self.table = RoutesetterTable()
        else:
            self.table = RoutesetterTable(table_path)
        self.logger = logger or logging.getLogger(__name__)
        self.ADMIN_START, self.AWAIT_CONTEST, self.AWAIT_SETTER, self.AWAIT_PEOPLE = range(4)
        self.START, self.AWAIT_RESULT = range(2)
        self.activity = None

    @is_setters_chat
    def setter_menu(self, update: Update, context: CallbackContext) -> None:
        message = update.effective_message.text
        user = update.effective_user.username.strip().lower()
        self.logger.info(f'{user} wrote the command "{message}"')
        keyboard = [[InlineKeyboardButton('Таблица накрутки', callback_data='1')],
                    [InlineKeyboardButton('Сколько я накрутил', callback_data='2')],
                    [InlineKeyboardButton('Кто в этом месяце накрутил больше всех', callback_data='3')],
                    [InlineKeyboardButton('Внести свои результаты', callback_data='4')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please choose:', reply_markup=reply_markup)
        self.logger.info('Bot offered a menu')
        return self.START

    def menu_option(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        user = query.from_user.username.strip().lower()
        query.edit_message_text(text=f"Выбранный вариант: {query.data}.")
        self.logger.info(f'{user} has selected "{query.data}"')

    def handle_setting_table(self, update: Update, context: CallbackContext):
        self.menu_option(update, context)
        with self.table.get_table_as_bytes() as f:
            context.bot.send_document(update.effective_chat.id, f, filename='Routesetting.xlsx')
        context.bot.send_message(chat_id=update.effective_chat.id, text="Это таблица накрутки.")
        self.logger.info('bot sent the table excel file')
        return ConversationHandler.END

    def handle_results(self, update: Update, context: CallbackContext):
        try:
            self.menu_option(update, context)
            user = update.effective_user.username.strip().lower()
            user_result = self.table.get_user_result(f'@{user}')
            mes_text = 'Ты не рутсеттер в ClimbLab.'
            if user_result:
                result = '\n'.join(user_result)
                mes_text = f'{user}, твои трассы за этот месяц:\n{result}'
                self.logger.info(f'bot sent the {user}\'s results')
        except Exception as e:
            self.logger.error(f'Error while reading excel table\n {e}')
            mes_text = 'Error while reading excel table'
        context.bot.send_message(chat_id=update.effective_chat.id, text=mes_text)
        return ConversationHandler.END

    def handle_the_richest(self, update: Update, context: CallbackContext):
        try:
            self.menu_option(update, context)
            richest = self.table.richest_user()
            mes_text = "Вы не крутили в этом месяце."
            if len(richest) == 1:
                mes_text = f'Самый богатый сеттер: {richest[0]}, ему(ей) нужен отдых :)'
            elif len(richest) > 1:
                names = ', '.join([i for i in richest])
                mes_text = f'{names} самые богатые. Им нужен отдых :)'
            self.logger.info(f'bot sent the message about the richest')
        except Exception as e:
            self.logger.error(f'Error while reading excel table\n {e}')
            mes_text = 'Error while reading excel table'
        context.bot.send_message(chat_id=update.effective_chat.id, text=mes_text)
        return ConversationHandler.END

    def handle_additional_results(self, update: Update, context: CallbackContext):
        self.menu_option(update, context)
        message = '''Введите (ОТВЕТОМ НА ЭТО СООБЩЕНИЕ) свои результаты в формате: DD.MM.YYYY a b c d e
Где a b c d - количество трасс категорий: 5 6а 6бс 7абс Джокер
Например: 21.04.2022 1 2 1 0 0
Если в тот день уже есть результаты, введенные сейчас результаты встанут на их место'''
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        return self.AWAIT_RESULT

    def add_single_results(self, update: Update, context: CallbackContext):
        try:
            message = update.effective_message.text
            username = f'@{update.effective_user.username.strip().lower()}'
            date, *amounts = message.split()
            for i in range(len(amounts)):
                status = self.table.add_result(date, username, i, int(amounts[i])).value
                if status == ResultStatus.FAIL_TO_GET_DATE.value:
                    context.bot.send_message(update.effective_chat.id, text=f'Такой даты ({date}) нет в текущем месяце')
                    return ConversationHandler.END
                if status == ResultStatus.NOT_SETTER.value:
                    context.bot.send_message(update.effective_chat.id, text=f'{username}, ты не накрутчик')
                    return ConversationHandler.END
            context.bot.send_message(update.effective_chat.id, text='Результаты добавлены. Ты можешь проверить их, посмотрев таблицу накрутки (/menu)')
        except Exception as e:
            self.logger.error(f'Error while reading excel table\n {e}')
            context.bot.send_message(update.effective_chat.id, text='Error while reading excel table')
        return ConversationHandler.END

    @is_setters_chat
    def admin_menu(self, update: Update, context: CallbackContext):
        if not is_admin_message(update, context):
            update.message.reply_text(f'Ты не Босс. Только он может написать {update.effective_message.text}')
            return
        keyboard = [[InlineKeyboardButton('Добавить рутсеттера', callback_data='add_setter')],
                    [InlineKeyboardButton('Удалить рутсеттера', callback_data='remove_setter')],
                    [InlineKeyboardButton('Добавить контест', callback_data='add_contest')],
                    [InlineKeyboardButton('Удалить последний добавленный контест', callback_data='remove_contest')],
                    [InlineKeyboardButton('Изменить накрутку на следующей(или уже этой) неделе', callback_data='change')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please choose:', reply_markup=reply_markup)
        self.logger.info('Bot offered an admin_menu')
        return self.ADMIN_START

    def add_setter_button(self, update: Update, context: CallbackContext):
        info = get_button_tap_info(update)
        chat_id = info['chat_id']
        if is_admin_choice(context, info):
            context.bot.send_message(chat_id, text='Введите (ОТВЕТОМ НА ЭТО СООБЩЕНИЕ) рутсеттера которого нужно добавить: @сеттер')
            self.activity = True
            return self.AWAIT_SETTER
        return self.ADMIN_START

    def remove_setter_button(self, update: Update, context: CallbackContext):
        info = get_button_tap_info(update)
        chat_id = info['chat_id']
        if is_admin_choice(context, info):
            context.bot.send_message(chat_id, text='Введите (ОТВЕТОМ НА ЭТО СООБЩЕНИЕ) рутсеттера которого нужно удалить: @сеттер')
            self.activity = False
            return self.AWAIT_SETTER
        return self.ADMIN_START

    def choose_setter(self, update: Update, context: CallbackContext):
        bot_mes = 'ERROR while adding/removing setter'
        setter_name = update.effective_message.text.strip().lower()
        self.logger.info(f'Owner sent "{setter_name}"')
        if self.activity:
            status = self.table.add_setter(setter_name).value
            if status == SetterStatus.ADDED.value:
                bot_mes = f'Сеттер {setter_name} успешно добавлен'
            elif status == SetterStatus.ALREADY_EXISTS.value:
                bot_mes = f'Сеттер {setter_name} уже есть в таблице. Попробуйте снова (/admin_menu)'
            context.bot.send_message(update.effective_chat.id, text=bot_mes)
            return ConversationHandler.END
        status = self.table.remove_setter(setter_name).value
        if status == SetterStatus.REMOVED.value:
            bot_mes = f'Сеттер {setter_name} удален'
        elif status == SetterStatus.NOT_FOUND.value:
            bot_mes = f'Сеттер {setter_name} не был найден. Попробуйте снова (/admin_menu)'
        context.bot.send_message(update.effective_chat.id, text=bot_mes)
        return ConversationHandler.END

    def add_contest_button(self, update: Update, context: CallbackContext):
        message = 'Введите(ОТВЕТОМ НА ЭТО СООБЩЕНИЕ) инфо о контесте в формате: DD.MM.YYYY название(on English) оплата\nНапример:\n21.04.2022 slabfest 1500'
        info = get_button_tap_info(update)
        chat_id = info['chat_id']
        if is_admin_choice(context, info):
            context.bot.send_message(chat_id, text=message)
            return self.AWAIT_CONTEST
        return self.ADMIN_START

    def add_contest_info(self, update: Update, context: CallbackContext):
        try:
            message = 'Введите(ОТВЕТОМ НА ЭТО СООБЩЕНИЕ) рутсеттеров которые крутят контест в формате: @setter1 @setter2\nНапример:\n@rutserser @nerutserser'
            contest_date, contest_name, contest_money = update.effective_message.text.split()
            status = self.table.add_contest(f"_{contest_date}", contest_name, int(contest_money)).value
            if status == ContestStatus.ADDED.value:
                context.bot.send_message(update.effective_chat.id, text=f'Данные о контесте успешно добавлены\n{message}')
                return self.AWAIT_PEOPLE
            if status == ContestStatus.NO_PLACE.value:
                context.bot.send_message(update.effective_chat.id, text='Уже есть два контеста в этом месяце. Добавить новый пока невозможно(')
                return ConversationHandler.END
        except Exception as e:
            self.logger.error(f'Error while reading excel table\n {e}')
            context.bot.send_message(update.effective_chat.id, text='Error while reading excel table')
            return ConversationHandler.END

    def add_contest_setters(self, update: Update, context: CallbackContext):
        try:
            setters = update.effective_message.text.split()
            self.logger.info(f'Owner sent "{setters}"')
            for setter in setters:
                status = self.table.add_contest_setter(setter.lower().strip()).value
                if status == ContestStatus.IS_CONTEST_SETTER.value:
                    context.bot.send_message(update.effective_chat.id, text=f'Сеттер {setter} будет крутить контест')
                    time.sleep(0.9)
                    continue
                if status == ContestStatus.SETTER_ABSENT.value:
                    context.bot.send_message(update.effective_chat.id, text=f'Сеттеру {setter} не добавлен контест. Его нет в таблице. Попробуйте добавить его еще раз')
                    message = 'Введите(ОТВЕТОМ НА ЭТО СООБЩЕНИЕ) рутсеттеров которые еще не добавлены, в формате: @setter1 @setter2\nНапример:\n@rutserser @nerutserser'
                    context.bot.send_message(update.effective_chat.id, text=message)
                    return self.AWAIT_PEOPLE
        except Exception as e:
            self.logger.error(f'Error while reading excel table\n {e}')
            context.bot.send_message(update.effective_chat.id, text='Error while reading excel table. Try again')
        return ConversationHandler.END

    def remove_contest_button(self, update: Update, context: CallbackContext):
        try:
            message = 'Последний добавленный контест удален'
            info = get_button_tap_info(update)
            chat_id = info['chat_id']
            if is_admin_choice(context, info):
                status = self.table.remove_contest().value
                if status == ContestStatus.REMOVED.value:
                    context.bot.send_message(chat_id, text=message)
                if status == ContestStatus.NO_CONTEST.value:
                    context.bot.send_message(chat_id, text='В таблице нет контестов')
                return ConversationHandler.END
            return self.ADMIN_START
        except Exception as e:
            self.logger.error(f'Error while reading excel table\n {e}')
            context.bot.send_message(update.effective_chat.id, text='Error while reading excel table. Try again')
            return ConversationHandler.END

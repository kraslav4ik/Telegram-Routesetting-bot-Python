import logging
import datetime
import time
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from Storage import Storage, AddResStatus, AddSetterStatus, GetResStatus


WEEKDAYS = {0: "Пн", 1: "Вт", 2: "Ср", 3: "Чт", 4: "Пт", 5: "Сб", 6: "Вс"}


class SettingProcess(object):

    def __init__(self, storage: Storage = None, logger=None):
        self.setting_days = {"first": 1, "second": 3}
        self.storage = storage or Storage()
        self.logger = logger or logging.getLogger(__name__)
        self.AWAIT_DATE = 2
        self.AWAIT_DAYS = 2
        self.AWAIT_RESULTS = 2

    def start(self, update: Update, context: CallbackContext) -> None:
        try:
            chat_id = update.effective_chat.id
            if context.job_queue.get_jobs_by_name('weekly_job'):
                self.logger.info('Default jobs are already exist and will not be added again')
                context.bot.send_message(update.effective_chat.id, "Bot is already working")
                return
            context.job_queue.run_daily(
                self.new_week, context=chat_id, name='new_week',
                time=datetime.time(hour=9, minute=00, second=00), days=(6,)
            )
            self.logger.info("Bot is launched")
            context.bot.send_message(update.effective_chat.id, "Monitoring of setting process is Launched\n"
                                                               "Now let's add setters")
            self.add_setter_button(update, context)

        except Exception as e:
            self.logger.error(e)

    def new_week(self, context: CallbackContext) -> None:
        chat_id = int(''.join([str(job.context) for job in context.job_queue.get_jobs_by_name('new_week')]))
        self.logger.info(
            'There is a sunday(or owner wants to change days), bot offered to choose the setting day(s)')
        first_setting_day_name = WEEKDAYS[self.setting_days["first"]]
        second_setting_day_name = WEEKDAYS[self.setting_days["second"]]
        keyboard = [[InlineKeyboardButton(first_setting_day_name, callback_data=f'WJ_{self.setting_days["first"]}')],
                    [InlineKeyboardButton(second_setting_day_name, callback_data=f'WJ_{self.setting_days["second"]}')],
                    [InlineKeyboardButton(f'{first_setting_day_name} + {second_setting_day_name}',
                                    callback_data=f'WJ_{self.setting_days["first"]}_{self.setting_days["second"]}')],
                    [InlineKeyboardButton('Не крутим', callback_data='WJ_')],
                    [InlineKeyboardButton('Изменить дни', callback_data='WJ_custom')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id, text='Когда будем крутить на следующей неделе?',
                                 reply_markup=reply_markup)
        job_removed = self.remove_job('weekly job', context)
        mes = 'Bot offered a menu with weekly work'
        if job_removed:
            mes += ' and old weekly work is deleted'
        self.logger.info(mes)

    def remove_job(self, name: str, context: CallbackContext) -> bool:
        current_week_jobs = context.job_queue.get_jobs_by_name(name)
        if not current_week_jobs:
            return False
        for job in current_week_jobs:
            job.schedule_removal()
        return True

    def handle_days(self, update: Update, context: CallbackContext):
        try:
            query = update.callback_query
            days_str = query.data.split('_')[1:]
            if not days_str:
                self.logger.info("no settings on next week")
                return
            days = [int(i) for i in days_str]  # get callback day
            chat_id = update.effective_chat.id

            for day in days:
                date = self.get_date_by_weekday(day)
                self.storage.add_setting(date)
                period = datetime.datetime(year=date.year, month=date.month, day=date.day, hour=10, minute=0, second=0)
                if context.job_queue.get_jobs_by_name(f"setting {date}"):
                    self.logger.info(f'Job for setting on {date} already exists')
                    continue
                context.job_queue.run_once(self.send_after_setting_poll, period,
                                           context={"chat": chat_id, "date": date}, name=f"setting {date}")
                self.logger.info(f"created job for setting {date}")

            query.edit_message_text(text=f"Выбранный вариант: {query.data}.")
            self.logger.info(f'Owner selected "{query.data}"')
            poll_options = [WEEKDAYS[day] for day in days] + ["Не кручу"]
            context.bot.sendPoll(chat_id, 'Кручу в...?', poll_options, is_anonymous=False, allows_multiple_answers=False)
        except Exception as e:
            self.logger.error(e)

    def get_date_by_weekday(self, day) -> datetime.date:
        today = datetime.date.today()
        for i in range(7):
            cur_day = (today + datetime.timedelta(days=i))
            day_num = cur_day.weekday()
            if day_num == day:
                return cur_day
        self.logger.error("DATE ERROR")

    def send_after_setting_poll(self, context: CallbackContext):
        try:
            job = context.job
            chat_id = job.context["chat"]
            date = job.context["date"]
            context.bot.send_message(chat_id, text='Накрутка с каждым днем все лучше. Не забудьте внести результаты')
            context.bot_data.update({})
            words = self.storage.grades
            options = ['0', '1', '2', '3', '4', '5']
            payloads = defaultdict(dict)
            for grade in words:
                message = context.bot.send_poll(chat_id, f'Сколько {grade} ?', options, is_anonymous=False,
                                                allows_multiple_answers=False)
                payload = {
                    "date": date,
                    "grade": grade,
                    "options": options,
                    "chat_id": chat_id
                }
                payloads[message.poll.id] = payload
                time.sleep(0.9)
            context.bot_data.update(payloads)
        except Exception as e:
            self.logger.error(e)

    def receive_after_setting_poll(self, update: Update, context: CallbackContext) -> None:
        try:
            answer = update.poll_answer
            poll_id = answer.poll_id
            if poll_id not in context.bot_data:
                return
            selected_options = answer.option_ids
            tg_id = answer.user.id
            username = answer.user.username
            options = context.bot_data[poll_id]["options"]
            grade = context.bot_data[poll_id]["grade"]
            date = context.bot_data[poll_id]["date"]
            for option_id in selected_options:
                status = self.storage.add_single_res(tg_id, grade, int(options[option_id]), date).value
                if status == AddResStatus.USER_NOT_SETTER.value:
                    mes_text = f'{username}, твой результат: {grade} : {int(options[option_id])} не добавлен потому что ты не рутсеттер'
                    context.bot.send_message(context.bot_data[poll_id]["chat_id"], text=mes_text)
                if status == AddResStatus.NO_SETTING.value:
                    mes_text = f'{username}, твой результат: {grade} : {int(options[option_id])} не добавлен: ERROR'
                    context.bot.send_message(context.bot_data[poll_id]["chat_id"], text=mes_text)
                if status == AddResStatus.SUCCESS.value:
                    self.logger.info(f"added result {username} {grade}: {int(options[option_id])}")
        except Exception as e:
            self.logger.error(e)

    def end_period(self, update: Update, context: CallbackContext) -> ConversationHandler.END:
        setters_res, settings_res = self.storage.period_end()
        chat_id = update.effective_chat.id
        users = {}
        setters_mes = "Результаты за месяц:\n"
        for setter in setters_res:
            if setters_res[setter]:
                chat_member = context.bot.get_chat_member(chat_id, setter)
                username = chat_member.user.username
                users[setter] = f"@{username}"
                setters_mes += f'\n@{username}:\n'
                for grade in sorted(setters_res[setter]):
                    setters_mes += f'        {grade}: {setters_res[setter][grade]}\n'
        context.bot.send_message(chat_id, text=setters_mes)
        setting_mes = "Накрутки за этот месяц:"
        for setting in settings_res:
            setting_mes += f"\n{setting}: "
            setting_mes += ", ".join([users[setter] for setter in settings_res[setting]])
        context.bot.send_message(chat_id, setting_mes)
        return ConversationHandler.END

    def change(self, update: Update, context: CallbackContext):
        return

    def add_setter_button(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        keyboard = [[InlineKeyboardButton("Я рутсеттер", callback_data="add_setter")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id, text='Кликни если ты рутсеттер', reply_markup=reply_markup)
        return ConversationHandler.END

    def remove_setter_button(self, update: Update, context: CallbackContext):
        return

    def add_setter(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        query = update.callback_query
        status = self.storage.add_setter(user_id).value

        if status == AddSetterStatus.ALREADY_EXISTS.value:
            query.answer(text='Ты уже есть в списке накрутчиков')
        if status == AddSetterStatus.ADDED.value:
            query.answer(text='Ты добавлен(а) в список накрутчиков CL')

    def show_user_res(self, update: Update, context: CallbackContext) -> ConversationHandler.END:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        username = update.effective_user.username
        res = self.storage.get_single_res(user_id)
        if res[0].value == GetResStatus.USER_NOT_SETTER:
            context.bot.send_message(chat_id, 'Ты не рутсеттер')
            return ConversationHandler.END
        res_string = '\n'.join([f'{i}, {res[i]}' for i in res[1]])
        if not res_string:
            context.bot.send_message(chat_id, f'{username}, ты не крутил(а) в этом месяце')
            self.logger.info(f'Bot sent {username} results')
            return ConversationHandler.END
        context.bot.send_message(chat_id, f'{username}, твои результаты:\n{res_string}')
        self.logger.info(f"Bot sent {username}'s results")
        return ConversationHandler.END

    def handle_richest(self):
        pass

    def add_single_res_button(self):
        pass








import datetime
import logging
import time
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from utils import get_button_tap_info, is_admin_choice, is_setters_chat
from TableTools import RoutesetterTable, ResultStatus


class Scheduler:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.table = RoutesetterTable()

    @is_setters_chat
    def set_default_jobs(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_chat.id
        if context.job_queue.get_jobs_by_name('new_month'):
            self.logger.info('Default jobs are already exist and will not be added again')
            return
        # context.job_queue.run_once(self.new_month, 5, context=chat_id, name='new_month')
        context.job_queue.run_monthly(self.new_month, context=chat_id, name='new_month', when=datetime.time(hour=9, minute=00, second=00), day=30)
        # context.job_queue.run_once(self.new_week, 5, context=chat_id, name='new_week')
        # context.job_queue.run_monthly(self.new_month, context=chat_id, name='new_month', when=datetime.time(hour=16, minute=35, second=30), day=9)
        context.job_queue.run_daily(self.new_week, context=chat_id, name='new_week', time=datetime.time(hour=9, minute=00, second=00), days=(6,))
        # context.job_queue.run_daily(self.new_week, context=chat_id, name='new_week', time=datetime.time(hour=16, minute=31, second=30), days=(3,))
        context.job_queue.run_daily(self.new_day, context=chat_id, name='new_day', time=datetime.time(hour=00, minute=00, second=00), days=(0, 1, 2, 3, 4, 5, 6))
        self.logger.info('monthly, weekly and daily jobs are added to the job_queue')

    def new_month(self, context: CallbackContext) -> None:
        context.bot.send_message(context.job.context, text='Текущий месяц подходит к концу')
        self.table.new_sheet()
        results = self.table.get_month_result()
        if not results:
            context.bot.send_message(context.job.context, text='Error had happened while reading Excel.')
            return
        context.bot.send_message(context.job.context, text='Вот результаты за этот месяц. Проверяйте')
        for key in results:
            result = '\n'.join(results[key])
            context.bot.send_message(context.job.context, text=f'{key}\n{result}')
            time.sleep(1)
        self.logger.info('Bot shown the month results')

    def new_day(self, _: CallbackContext) -> None:
        self.logger.info('Bot got the new day')
        return self.table.on_scheduler_new_day()

    def new_week(self, context: CallbackContext) -> None:
        chat_id = int(''.join([str(job.context) for job in context.job_queue.get_jobs_by_name('new_week')]))
        self.logger.info('There is a sunday(or owner wants to change days), bot offered to choose the setting day(s)')
        keyboard = [[InlineKeyboardButton('Вторник', callback_data='ВТ')],
                    [InlineKeyboardButton('Четверг', callback_data='ЧТ')],
                    [InlineKeyboardButton('Вторник+Четверг', callback_data='ВТ+ЧТ')],
                    [InlineKeyboardButton('Не крутим', callback_data='Нет')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id, text='Когда будем крутить на следующей неделе?', reply_markup=reply_markup)
        job_removed = self.remove_job('weekly job', context)
        mes = 'Bot offered a menu with weekly work'
        if job_removed:
            mes += ' and old weekly work is deleted'
        self.logger.info(mes)

    def handle_weekly_schedule(self, context: CallbackContext, days, chat_id, query) -> None:
        if days:
            # context.job_queue.run_once(self.setting_result, 5, context=chat_id)
            # context.job_queue.run_daily(self.setting_result, context=chat_id, name='weekly job', time=datetime.time(hour=14, minute=25, second=30), days=(4,))
            context.job_queue.run_daily(self.setting_result, context=chat_id, name='weekly job', time=datetime.time(hour=10, minute=00, second=00), days=days)
            message = 'new weekly work added'
        else:
            message = 'no added work this week'
        self.logger.info(message)
        query.edit_message_text(text=f"Выбранный вариант: {query.data}.")
        self.logger.info(f'Owner selected "{query.data}"')

    def remove_job(self, name: str, context: CallbackContext) -> bool:
        current_week_jobs = context.job_queue.get_jobs_by_name(name)
        if not current_week_jobs:
            return False
        for job in current_week_jobs:
            job.schedule_removal()
        return True

    def handle_tuesday(self, update: Update, context: CallbackContext) -> None:
        info = get_button_tap_info(update)
        chat_id = info['chat_id']
        if is_admin_choice(context, info):
            days = (1,)
            self.handle_weekly_schedule(context, days, chat_id, info['query'])
            self.weekly_poll(context, chat_id, ['Кручу во Вторник', 'Не кручу'])

    def handle_thursday(self, update: Update, context: CallbackContext) -> None:
        info = get_button_tap_info(update)
        chat_id = info['chat_id']
        if is_admin_choice(context, info):
            days = (3,)
            self.handle_weekly_schedule(context, days, chat_id, info['query'])
            self.weekly_poll(context, chat_id, ['Кручу в Четверг', 'Не кручу'])

    def handle_tt(self, update: Update, context: CallbackContext) -> None:
        info = get_button_tap_info(update)
        chat_id = info['chat_id']
        if is_admin_choice(context, info):
            days = (1, 3)
            self.handle_weekly_schedule(context, days, chat_id, info['query'])
            self.weekly_poll(context, chat_id, ['Вторник', 'Четверг'])

    def handle_not(self, update: Update, context: CallbackContext) -> None:
        info = get_button_tap_info(update)
        chat_id = info['chat_id']
        if is_admin_choice(context, info):
            days = ()
            self.handle_weekly_schedule(context, days, chat_id, info['query'])

    def setting_result(self, context: CallbackContext) -> None:
        job = context.job
        context.bot.send_message(job.context, text='Накрутка с каждым днем все лучше. Не забудьте внести результаты')
        self.after_setting_poll(context, job.context)

    def weekly_poll(self, context: CallbackContext, chat_id, days) -> None:
        context.bot.send_poll(chat_id, 'Когда крутим?', days, is_anonymous=False, allows_multiple_answers=True)

    def after_setting_poll(self, context: CallbackContext, chat_id) -> None:
        context.bot_data.update({})
        words = ['5', '6a', '6bc', '7abc', 'джокеров']
        options = ['0', '1', '2', '3', '4', '5']
        payloads = defaultdict(dict)
        for i in range(len(words)):
            message = context.bot.send_poll(chat_id, f'Сколько {words[i]} ?', options, is_anonymous=False, allows_multiple_answers=False)
            payload = {
                    "data": self.table.current_date,
                    "grade": i,
                    "options": options,
                    "message_id": message.message_id,
                    "chat_id": chat_id
                    }
            payloads[message.poll.id] = payload
            time.sleep(0.9)
        context.bot_data.update(payloads)

    def receive_after_setting_poll(self, update: Update, context: CallbackContext) -> None:
        try:
            answer = update.poll_answer
            poll_id = answer.poll_id
            if poll_id not in context.bot_data:
                return
            selected_options = answer.option_ids
            username = f"@{answer.user.username.strip().lower()}"
            options = context.bot_data[poll_id]["options"]
            grade = context.bot_data[poll_id]["grade"]
            date = context.bot_data[poll_id]["data"]
            for option_id in selected_options:
                status = self.table.add_result(date, username, grade, int(options[option_id])).value
                if status == ResultStatus.NOT_SETTER.value:
                    mes_text = f'{username}, твой результат: {grade} : {int(options[option_id])} не добавлен потому что ты не рутсеттер'
                    context.bot.send_message(context.bot_data[poll_id]["chat_id"], text=mes_text)
                if status == ResultStatus.FAIL_TO_GET_DATE.value:
                    mes_text = f'{username}, один из твоих результатов не добавлен'
                    context.bot.send_message(context.bot_data[poll_id]["chat_id"], text=mes_text)
        except Exception as e:
            self.logger.error(f'Error while reading excel table\n {e}')

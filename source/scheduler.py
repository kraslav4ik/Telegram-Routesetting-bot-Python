import logging
import datetime
import time
from telegram.ext import CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from setting_process import ClimbLabRouteSetter, SettingMonth


MONTHS = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul',
          8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
          }


class Scheduler(object):

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.__set_date()
        self.current_setting_month = SettingMonth(MONTHS[self.current_month], self.current_month)

    def __set_date(self) -> None:
        self.current_day = datetime.date.today().day
        self.current_month = datetime.date.today().month
        self.current_year = datetime.date.today().year
        self.current_date = datetime.date(self.current_year, self.current_month, self.current_day).strftime('%d.%m.%Y')
        self.next_month = self.current_month + 1
        self.next_year = self.current_year + 1
        self.year_to_use = self.current_year
        if self.current_month == 12:
            self.next_month = 1
            self.year_to_use = self.current_year + 1

    def set_default_jobs(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_chat.id
        if context.job_queue.get_jobs_by_name('new_month'):
            self.logger.info('Default jobs are already exist and will not be added again')
            return
        context.job_queue.run_monthly(self.new_month, context=chat_id, name='new_month', when=datetime.time(hour=9, minute=00, second=00), day=SettingMonth.current_month.result_day)
        context.job_queue.run_daily(self.new_day, context=chat_id, name='new_day', time=datetime.time(hour=00, minute=00, second=00), days=(0, 1, 2, 3, 4, 5, 6))
        self.logger.info('daily job is added to the job_queue')

    def new_day(self) -> None:
        self.__set_date()
        self.logger.info(f'New day had begun. Today is {self.current_date}, next month is {self.next_month}')

    def new_month(self, context: CallbackContext):
        context.bot.send_message(context.job.context, text='Вот результаты за этот месяц. Проверяйте')
        for setter in ClimbLabRouteSetter.setters_info:
            result = setter.new_month()
            if not result:
                context.bot.send_message(context.job.context, text=f'Error with {setter.username} results.')
                time.sleep(1)
            context.bot.send_message(context.job.context, text=f'{setter.username}\n{result}')
            time.sleep(1)
        self.logger.info('Bot shown month results')

        del SettingMonth.current_month

        # СДЕЛАТЬ ПОЛЛ О ДНЕ РЕЗУЛЬТАТОВ

        self.current_setting_month = SettingMonth(MONTHS[self.next_month], self.next_month)

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

    def remove_job(self, name: str, context: CallbackContext) -> bool:
        current_week_jobs = context.job_queue.get_jobs_by_name(name)
        if not current_week_jobs:
            return False
        for job in current_week_jobs:
            job.schedule_removal()
        return True

    def weekly_job(self):
        pass

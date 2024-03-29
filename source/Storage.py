import datetime
import logging
from collections import defaultdict
from routesetting_parts import ClimbLabRouteSetter, ClimbLabSetting
from MySQL_scripts import SQLScripts
from enum import Enum


class AddResStatus(Enum):
    NO_SETTING = 1
    USER_NOT_SETTER = 2
    SUCCESS = 3


class AddSetterStatus(Enum):
    ALREADY_EXISTS = 1
    ADDED = 2
    TABLE_ERROR = 3

class GetResStatus(Enum):
    USER_NOT_SETTER = 1
    SUCCESS = 2


class Storage(object):

    def __init__(self, logger=None, path=None):
        db_info_path = path or "../data/database_info"
        self.logger = logger or logging.getLogger(__name__)
        self.table = SQLScripts(db_info_path)
        self.__get_all_table_info()
        self.logger.info('STORAGE INITIALIZED')

    def __get_all_table_info(self) -> None:
        self.grades = self.table.get_grades()
        users_list = self.table.get_users_info()
        setting_list = self.table.get_settings_info()
        self.users = [
            ClimbLabRouteSetter(telegram_id=user["tg_id"],
                                boulders=user["boulders"]) for user in users_list]
        self.settings = [
            ClimbLabSetting(setting_date=setting["date"],
                            boulders=setting["users"]) for setting in setting_list]
        # print(self.users)
        # print(self.settings)

    def add_setting(self, date: datetime.date) -> None:
        setting = next((setting for setting in self.settings if setting.date == date), None)
        if setting:
            self.logger.info(f'Setting with date {date} already exists')
            return
        self.settings.append(ClimbLabSetting(setting_date=date))
        self.table.add_setting(date)

    def add_single_res(self, tg_id: int, grade: str, amount: int, date: datetime.date) -> AddResStatus:
        setting = next((setting for setting in self.settings if setting.date == date), None)
        user = next((user for user in self.users if user.telegram_id == tg_id), None)
        if not setting:
            self.logger.info("user voted in setting which is not exists")
            return AddResStatus.NO_SETTING
        if not user:
            self.logger.info("Non-routesetter voted")
            return AddResStatus.USER_NOT_SETTER
        self.table.add_res(tg_id, grade, amount, setting.date)
        setting.boulders[user][grade] = amount
        user.boulders[grade] += amount
        return AddResStatus.SUCCESS

    def add_setter(self, tg_id: int) -> AddSetterStatus:
        setter_exists = next((user for user in self.users if user.telegram_id == tg_id), None)
        if setter_exists:
            self.logger.info(f'setter {tg_id} already exists')
            return AddSetterStatus.ALREADY_EXISTS
        self.users.append(ClimbLabRouteSetter(telegram_id=tg_id))
        added_to_table = self.table.add_setter(tg_id)
        if added_to_table:
            self.logger.info(f'setter {tg_id} added successfully')
            return AddSetterStatus.ADDED
        return AddSetterStatus.TABLE_ERROR

    def period_end(self) -> tuple:
        month_setter_res = {}
        month_settings_res = {}
        for setter in self.users:
            month_setter_res.update(setter.show_setter_info())
            setter.boulders = None
        for setting in self.settings:
            month_settings_res.update(setting.show_setting_info())
        self.settings = []
        self.table.period_end()
        return month_setter_res, month_settings_res

    def get_single_res(self, tg_id: int):
        setter = next((user for user in self.users if user.telegram_id == tg_id), None)
        if not setter:
            self.logger.info("Non-routesetter asked his results")
            return AddResStatus.USER_NOT_SETTER, defaultdict()
        res = setter.show_setter_info()[setter.telegram_id]
        return AddResStatus.SUCCESS, res


# s = Storage()
# s.add_setting(date=datetime.date.today())
# s.add_single_res(tg_id=401528773, grade='7abc', amount=3, date=datetime.date.today())
# s.add_single_res(tg_id=401528773, grade='5', amount=1, date=datetime.date.today())
# s.add_single_res(tg_id=401528773, grade='6a', amount=2, date=datetime.date.today())
# s.add_single_res(tg_id=401528773, grade='J', amount=3, date=datetime.date.today())








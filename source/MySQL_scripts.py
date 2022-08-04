import datetime
from collections import defaultdict
import mysql.connector
from mysql.connector import errorcode
from typing import List, Dict
import logging


DEFAULT_BOULDERS_SALARIES = {'5': 500, '6a': 750, '6bc': 1000, '7abc': 1250, 'J': 1000}


class SQLScripts(object):
    def __init__(self, path, logger=None):
        self.path = path
        self.logger = logger or logging.getLogger(__name__)
        self.__connecting_to_server()

    def __connecting_to_server(self):
        try:
            with open(self.path) as db_info:
                strings = [string.strip() for string in db_info.readlines()]
            user, password, host, database_name = strings[0], strings[1], strings[2], strings[3]
            self.cnx = mysql.connector.connect(user=user, password=password, host=host)
            self.cursor = self.cnx.cursor(buffered=True)
            self.__using_database(database_name)
            self.__create_tables()
        except IndexError as e:
            self.logger.error(f"{e}: file with database info should contain 4 string")
        except mysql.connector.Error as er:
            self.logger.error(er)

    def __using_database(self, database_name):
        try:
            self.cursor.execute(f"USE {database_name}")
            self.logger.info(f"Using database {database_name}: success")
        except mysql.connector.Error as er:
            self.logger.info(f"Database {database_name} does not exists.")
            if er.errno == errorcode.ER_BAD_DB_ERROR:
                self.__create_database(self.cursor, database_name)
                self.logger.info(f"Database {database_name} created successfully.")
                self.cnx.database = database_name
                return
            self.logger.error(er)

    def __create_database(self, cursor, name):
        try:
            cursor.execute(f"CREATE DATABASE {name} DEFAULT CHARACTER SET 'utf16'")
        except mysql.connector.Error as err:
            self.logger.error(f"Failed creating database: {err}")

    def __create_tables(self):
        create_routes = ("CREATE TABLE routes("
                         "route_id INT NOT NULL AUTO_INCREMENT,"
                         "category VARCHAR(8) NOT NULL, price INT NOT NULL,"
                         "PRIMARY KEY (route_id));")
        create_users = ("CREATE TABLE users("
                        "telegram_id INT NOT NULL,"
                        "PRIMARY KEY (telegram_id));")
        create_contests = ("CREATE TABLE contests("
                           "contest_id INT NOT NULL AUTO_INCREMENT, cont_name VARCHAR(35), cont_date DATE,"
                           "PRIMARY KEY (contest_id));")
        create_settings = ("CREATE TABLE settings("
                           "setting_id INT NOT NULL AUTO_INCREMENT, set_date DATE, PRIMARY KEY (setting_id));")
        create_setting_users = ("CREATE TABLE setting_users("
                    "setting_id INT NOT NULL, user INT NOT NULL, category INT NOT NULL, count INT DEFAULT 0,"
                    "FOREIGN KEY (setting_id) REFERENCES settings(setting_id) ON UPDATE CASCADE ON DELETE CASCADE, "
                    "FOREIGN KEY (user) REFERENCES users(telegram_id) ON UPDATE CASCADE ON DELETE CASCADE, "
                    "FOREIGN KEY (category) REFERENCES routes(route_id) ON UPDATE CASCADE ON DELETE CASCADE)")
        create_contest_users = ("CREATE TABLE contest_users("
                    "contest_id INT NOT NULL, user INT NOT NULL, payment INT,"
                    "FOREIGN KEY (contest_id) REFERENCES contests(contest_id) ON UPDATE CASCADE ON DELETE CASCADE, "
                    "FOREIGN KEY (user) REFERENCES users(telegram_id) ON UPDATE CASCADE ON DELETE CASCADE);")
        create_global_results = ("CREATE TABLE global_results(grade INT NOT NULL, amount INT NOT NULL DEFAULT 0, "
                                 "FOREIGN KEY (grade) REFERENCES routes(route_id))")

        table_names = {"routes": create_routes, "users": create_users,
                       "contests": create_contests, "settings": create_settings,
                       "setting_users": create_setting_users, "contest_users": create_contest_users,
                       "global_results": create_global_results
                       }
        try:
            self.cursor.execute("SHOW TABLES")
            table_lst = [''.join(row) for row in self.cursor]
            for name in table_names:
                if table_lst and name in table_lst:
                    self.logger.info(f"table {name} already exists")
                    continue
                self.cursor.execute(table_names[name])
                self.logger.info(f"table {name} created successfully")
            self.cursor.execute("SELECT * FROM routes")
            routes_is_filled = bool([row for row in self.cursor])
            if not routes_is_filled:
                for grade in DEFAULT_BOULDERS_SALARIES:
                    self.cursor.execute(
                        f'INSERT INTO routes (category, price) VALUES ("{grade}", {DEFAULT_BOULDERS_SALARIES[grade]});')
                    self.cnx.commit()
                self.logger.info("table 'routes' is filled with DEFAULT GRADES AND PRICES")
        except Exception as e:
            self.logger.error(e)

    def get_users_info(self) -> List[Dict]:
        self.cursor.execute("SELECT route_id, category FROM routes")
        difficulties = {}
        for route_id, category in self.cursor:
            difficulties[route_id] = category
        self.cursor.execute("SELECT * FROM USERS")
        users = []
        for telegram_id in self.cursor:
            users.append({"tg_id": telegram_id[0]})
        for user in users:
            user["boulders"] = defaultdict(int)
            self.cursor.execute(f"SELECT category, count FROM setting_users WHERE user = {user['tg_id']}")
            for category, count in self.cursor:
                user["boulders"][difficulties[category]] += count
        return users

    def get_settings_info(self) -> List[Dict]:
        self.cursor.execute("SELECT route_id, category FROM routes")
        difficulties = {}
        for route_id, category in self.cursor:
            difficulties[route_id] = category
        self.cursor.execute("SELECT * FROM settings")
        settings = []
        for setting_id, set_date in self.cursor:
            settings.append({"date": set_date, "setting_id": setting_id})
        for setting in settings:
            setting["users"] = defaultdict(dict)
            self.cursor.execute(
                f"SELECT user, category, count FROM setting_users WHERE setting_id = {setting['setting_id']}")
            for user, category, count in self.cursor:
                setting["users"][user][difficulties[category]] = count
        for setting in settings:
            setting.pop("setting_id")
        return settings

    def get_grades(self):
        prices = {}
        self.cursor.execute("SELECT category, price FROM routes")
        for category, price in self.cursor:
            prices[category] = price
        return prices

    def add_setting(self, date: datetime.date):
        # self.cursor.execute(f"INSERT INTO settings (set_date) VALUES (STR_TO_DATE({date},'%Y-%m-%d'))")
        self.cursor.execute(f"INSERT INTO settings (set_date) VALUES ('{date}')")
        self.cnx.commit()

    def add_res(self, tg_id: int, grade: str, amount: int, setting_date: datetime.date):
        self.cursor.execute(f"INSERT INTO setting_users (setting_id, user, category, count) VALUES ("
                            f"(SELECT setting_id FROM settings WHERE set_date = '{setting_date}'),"
                            f"(SELECT telegram_id from users WHERE telegram_id = {tg_id}),"
                            f"(SELECT route_id FROM routes WHERE category = '{grade}'),"
                            f"{amount})")
        self.cnx.commit()

    def period_end(self):
        self.cursor.execute("SELECT route_id FROM routes")
        routes = [route_id[0] for route_id in self.cursor]
        for route_id in routes:
            self.cursor.execute(f"SELECT amount FROM global_results WHERE grade = {route_id}")
            prev_res = [amount for amount in self.cursor]
            if not prev_res:
                self.cursor.execute(f"INSERT INTO global_results(grade) VALUES({route_id})")
                self.cnx.commit()
                prev_res = 0
            else:
                prev_res = prev_res[0][0]
            self.cursor.execute(f"SELECT count FROM setting_users WHERE category = {route_id}")
            cur_res = [count for count in self.cursor]
            cur_res = 0 if not cur_res else cur_res[0][0]
            self.cursor.execute(f"UPDATE global_results SET amount = "
                                f"{prev_res} + {cur_res} "
                                f"WHERE grade = {route_id}")
            self.cnx.commit()
        self.cursor.execute("DELETE FROM setting_users")
        self.cursor.execute("DELETE FROM settings")
        self.cnx.commit()
        return

    def add_setter(self, tg_id):
        try:
            self.cursor.execute(f"INSERT INTO users VALUES ({tg_id})")
            self.cnx.commit()
            return True
        except mysql.connector.Error as e:
            self.logger.error(e)
            return False


# testcase = SQLScripts("../data/database_info")
# testcase.period_end()

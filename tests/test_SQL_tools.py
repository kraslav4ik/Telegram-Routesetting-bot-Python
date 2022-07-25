import datetime
import unittest

from collections import defaultdict

from source.MySQL_scripts import SQLScripts, DEFAULT_BOULDERS_SALARIES

TEST_PATH = '../data/test_database_info'
TABLES = {"routes", "users", "contests", "settings", "setting_users", "contest_users"}


class TestSQLTools(unittest.TestCase):

    def setUp(self):
        self.database = SQLScripts(path=TEST_PATH)

    def test_tables_creation(self):
        self.database.cursor.execute('DROP TABLE contest_users')
        self.database.cursor.execute('DROP TABLE setting_users')
        self.database.cursor.execute("SHOW TABLES")
        table_list = [''.join(table) for table in self.database.cursor]
        for table in table_list:
            self.database.cursor.execute(f'DROP TABLE {table}')
        self.database.cursor.execute("SHOW TABLES")
        table_list = [''.join(table) for table in self.database.cursor]
        self.assertEqual(table_list, [])
        self.database.__init__(path=TEST_PATH)
        self.database.cursor.execute("SHOW TABLES")
        table_list = [''.join(table) for table in self.database.cursor]
        self.assertEqual(set(table_list), TABLES)

        tables_rows = {"routes": {"Fields": ['route_id', 'category', 'price'],
                                  "Type": [b'int', b'varchar(8)', b'int'],
                                  "Null": ['NO', 'NO', 'NO'],
                                  "Key": ['PRI', '', ''],
                                  "Default": [None, None, None],
                                  "Extra": ['auto_increment', '', '']},
                       "users": {"Fields": ['telegram_id'],
                                 "Type": [b'int'],
                                 "Null": ['NO'],
                                 "Key": ['PRI'],
                                 "Default": [None],
                                 "Extra": ['']},
                       "contests": {"Fields": ['contest_id', 'cont_name', 'cont_date'],
                                 "Type": [b'int', b'varchar(35)', b'date'],
                                 "Null": ['NO', 'YES', 'YES'],
                                 "Key": ['PRI', '', ''],
                                 "Default": [None, None, None],
                                 "Extra": ['auto_increment', '', '']},
                       "settings": {"Fields": ['setting_id', 'set_date'],
                                 "Type": [b'int', b'date'],
                                 "Null": ['NO', 'YES'],
                                 "Key": ['PRI', ''],
                                 "Default": [None, None],
                                 "Extra": ['auto_increment', '']},
                       "setting_users": {"Fields": ['setting_id', 'user', 'category', 'count'],
                                 "Type": [b'int', b'int', b'int', b'int'],
                                 "Null": ['NO', 'NO', 'NO', 'YES'],
                                 "Key": ['MUL', 'MUL', 'MUL', ''],
                                 "Default": [None, None, None, b'0'],
                                 "Extra": ['', '', '', '']},
                       "contest_users": {"Fields": ['contest_id', 'user', 'payment'],
                                 "Type": [b'int', b'int', b'int'],
                                 "Null": ['NO', 'NO', 'YES'],
                                 "Key": ['MUL', 'MUL', ''],
                                 "Default": [None, None, None],
                                 "Extra": ['', '', '']}}
        for table in tables_rows:
            self.database.cursor.execute(f"SHOW COLUMNS FROM {table}")
            for i, (Field, Type, Null, Key, Default, Extra) in enumerate(self.database.cursor):
                self.assertEqual(Field, tables_rows[table]["Fields"][i])
                self.assertEqual(Type, tables_rows[table]["Type"][i])
                self.assertEqual(Null, tables_rows[table]["Null"][i])
                self.assertEqual(Key, tables_rows[table]["Key"][i])
                self.assertEqual(Default, tables_rows[table]["Default"][i])
                self.assertEqual(Extra, tables_rows[table]["Extra"][i])

        self.database.cursor.execute("SELECT category, price FROM routes")
        for boulder, (category, price) in zip(DEFAULT_BOULDERS_SALARIES, self.database.cursor):
            self.assertEqual(category, boulder)
            self.assertEqual(price, DEFAULT_BOULDERS_SALARIES[boulder])

    def test_add_setting(self):
        test_data = (datetime.date(year=2000, month=5, day=13), datetime.date(year=2022, month=5, day=13))
        expexted = test_data
        for date in test_data:
            self.database.add_setting(date)
        self.database.cursor.execute("SELECT (set_date) FROM settings")
        for date, expected_date in zip(self.database.cursor, expexted):
            self.assertEqual(date[0], expected_date)

    def test_add_res(self):
        test_data = self.insert_test_data()
        self.database.cursor.execute("SELECT setting_id FROM settings")
        expected_settings = [setting_id[0] for setting_id in self.database.cursor]
        expected_grades = []
        for i in range(2):
            self.database.cursor.execute(
                f"SELECT route_id FROM routes WHERE category = '{test_data['results'][i]['grade']}'")
            expected_grades.append([route_id for route_id in self.database.cursor][0][0])
        for i in range(2):
            self.database.cursor.execute(f"SELECT * FROM setting_users WHERE user = {test_data['setters'][i]}")
            for (setting_id, user, category, count) in self.database.cursor:
                exp_id = expected_settings[i]
                exp_user = test_data["setters"][i]
                exp_category = expected_grades[i]
                exp_amount = test_data["results"][i]["amount"]
                self.assertEqual(setting_id, exp_id)
                self.assertEqual(user, exp_user)
                self.assertEqual(category, exp_category)
                self.assertEqual(count, exp_amount)

    def insert_test_data(self):
        test_data = {"setters": [500, 600],
                     "settings": [datetime.date(year=2000, month=5, day=13), datetime.date(year=2022, month=5, day=13)],
                     "results": [
                         {"tg_id": 500, "grade": "J", "amount": 2, "date": datetime.date(year=2000, month=5, day=13)},
                         {"tg_id": 600, "grade": "6bc", "amount": 2, "date": datetime.date(year=2022, month=5, day=13)}
                         ]}
        for i in range(2):
            self.database.cursor.execute(f"INSERT INTO users VALUES ({test_data['setters'][i]})")
            self.database.cnx.commit()
            self.database.cursor.execute(f"INSERT INTO settings(set_date) VALUES ('{test_data['settings'][i]}')")
            self.database.cnx.commit()

        for i in range(2):
            tg_id = test_data["results"][i]["tg_id"]
            grade = test_data["results"][i]["grade"]
            amount = test_data["results"][i]["amount"]
            date = test_data["results"][i]["date"]
            self.database.add_res(tg_id=tg_id, grade=grade, amount=amount, setting_date=date)

        return test_data

    def test_get_users_get_settings_get_grades(self):
        test_data = self.insert_test_data()

        grades = []
        for i in range(2):
            self.database.cursor.execute(
                f"SELECT route_id FROM routes WHERE category = '{test_data['results'][i]['grade']}'")
            grades.append([route_id for route_id in self.database.cursor][0][0])

        expected_settings_res = [{"date": test_data["settings"][0], "users": defaultdict(dict)},
                                 {"date": test_data["settings"][1], "users": defaultdict(dict)}]
        expected_settings_res[0]["users"][500] = {"J": 2}
        expected_settings_res[1]["users"][600] = {"6bc": 2}
        expected_users_res = [{"tg_id": test_data['setters'][0], "boulders": defaultdict(int)},
                              {"tg_id": test_data['setters'][1], "boulders": defaultdict(int)}]
        expected_users_res[0]["boulders"]["J"] += 2
        expected_users_res[1]["boulders"]["6bc"] += 2
        expected_grades = DEFAULT_BOULDERS_SALARIES
        users = self.database.get_users_info()
        settings = self.database.get_settings_info()
        grades = self.database.get_grades()
        self.assertEqual(users, expected_users_res)
        self.assertEqual(settings, expected_settings_res)
        self.assertEqual(grades, expected_grades)

    def test_period_end(self):
        pass

    def tearDown(self) -> None:
        tables_to_clean = {"setting_users", "contest_users", "users", "contests", "settings"}
        for table in tables_to_clean:
            self.database.cursor.execute(f"DELETE FROM {table};")
            self.database.cnx.commit()


if __name__ == '__main__':
    unittest.main()

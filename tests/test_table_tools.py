import unittest
import datetime
import os
from pycel import ExcelCompiler
import sys
from freezegun import freeze_time

print(os.path.dirname(__file__))
fpath = os.path.join(os.path.dirname(__file__), '../src')
sys.path.append(fpath)
print(sys.path)

from TableTools import STARTS_FIRST_COL, LAST_DATE_COL, DATE_ROW, \
    SETTER_ROW_RANGE, SETTER_COLUMN, SALARY_COLUMN, RESULTS_COLUMN, MONTHS,\
    FIRST_CONTEST_COL, SECOND_CONTEST_COL, CONTEST_PRICE_ROW, CONTEST_NAME_ROW, SetterStatus, ContestStatus, ResultStatus


class TestTableTools(unittest.TestCase):

    @freeze_time('2022-05-13')
    def setUp(self) -> None:
        from TableTools import RoutesetterTable
        self.table = RoutesetterTable(path='../data/Routesetting-Test.xlsx')

    def test_init(self):
        self.assertEqual(self.table.current_date, datetime.date(2022, 5, 13).strftime('%d.%m.%Y'))

    def test_get_cell_val(self):
        for col in range(STARTS_FIRST_COL, LAST_DATE_COL + 1):
            with self.subTest(col=col):
                date = self.table.get_cell_val(self.table.current_month_name, DATE_ROW, col)
                if date is None:
                    continue
                self.assertRegex(date, r"\d{2}\.\d{2}\.20\d{2}")
        for row in range(*SETTER_ROW_RANGE):
            with self.subTest(row=row):
                setter_name = self.table.get_cell_val(self.table.current_month_name, row, SETTER_COLUMN)
                if not setter_name:
                    continue
                self.assertRegex(setter_name, r"@[A-z0-9_ -]+")

                salary = self.table.get_cell_val(self.table.current_month_name, row, SALARY_COLUMN)
                self.assertEqual(salary, 0)

                result = self.table.get_cell_val(self.table.current_month_name, row, RESULTS_COLUMN)
                self.assertEqual(result, 0)

    def test_get_setting_dates(self, month=5, year=2022, fst_tue_num=3):
        setting_dates = self.table.get_setting_dates(month, year)
        tuesdays = [(day, 1) for day in range(1, 32) if day % 7 == fst_tue_num]
        thursdays = [(day, 3) for day in range(1, 32) if day % 7 == fst_tue_num + 2]
        correct_dates = sorted(tuesdays + thursdays)
        self.assertEqual(setting_dates, correct_dates)

    def test_get_month_result(self):
        categories = ["{}: {}".format(a, b) for a, b in zip(('5', '6a', '6bc', '7abc', 'j', 'Contest'), ['0'] * 5 + [str(None)])]
        correct_res = {'@kraslav4ik': categories, '@ksenull': categories}
        results = self.table.get_month_result()
        self.assertEqual(results, correct_res)

    def test_new_sheet(self):
        for m, y, ftn in (6, 2022, 0), (1, 2023, 3):
            with self.subTest(m=m, y=y, ftn=ftn):
                self.table.new_sheet(month=m, year=y)

                sh_name = f'{y}. {m}. {MONTHS[m]}'
                self.assertIn(sh_name, self.table.workbook_r.sheetnames)
                expected_date = datetime.date(day=ftn + 2, month=m, year=y).strftime('%d.%m.%Y')
                actual_date = self.table.get_cell_val(sh_name, DATE_ROW, 4)
                self.assertEqual(actual_date, expected_date)

                self.table.workbook_w.remove(self.table.workbook_w[sh_name])
                self.table.workbook_w.save(self.table.tablepath)

    def test_get_salary_info(self):
        expected_dict = {'@kraslav4ik': 0, '@ksenull': 0}
        salary_dict = self.table.get_salary_info()
        self.assertEqual(salary_dict, expected_dict)

    def test_get_user_result(self):
        result = ["{}: {}".format(a, b) for a, b in zip(('5', '6a', '6bc', '7abc', 'j', 'Contest'), ['0'] * 5 + [str(None)])]
        expected_results = {'@kraslav4ik': result, '@ksenull': result, '@her_s_gory': [], '@jo': []}
        for user in expected_results:
            with self.subTest(user=user):
                actual_result = self.table.get_user_result(user)
                self.assertEqual(actual_result, expected_results[user])

    def test_richest_user(self):
        exp_col = 3
        exp_rows = (10, 16)
        test_data = {0: (None, None), 1: (3, None), 2: (None, 3), 3: (3, 3)}
        expected_result = {0: [], 1: ['@kraslav4ik'], 2: ['@ksenull'], 3: ['@kraslav4ik', '@ksenull']}
        for key in test_data:
            with self.subTest(data=test_data[key]):
                self.table.current_month_sh_w.cell(column=exp_col, row=exp_rows[0]).value = test_data[key][0]
                self.table.current_month_sh_w.cell(column=exp_col, row=exp_rows[1]).value = test_data[key][1]

                self.table.workbook_w.save(self.table.tablepath)
                self.table.workbook_f = ExcelCompiler(filename=self.table.tablepath)

                self.assertEqual(self.table.richest_user(), expected_result[key])

                self.table.current_month_sh_w.cell(column=exp_col, row=exp_rows[0]).value = None
                self.table.current_month_sh_w.cell(column=exp_col, row=exp_rows[1]).value = None
                self.table.workbook_w.save(self.table.tablepath)

    def test_add_setter(self):
        test_row = 18
        test_data = ['@kraslav4ik', '@her_s_gory']
        expected_result = {'@kraslav4ik': SetterStatus.ALREADY_EXISTS.value, '@her_s_gory': SetterStatus.ADDED.value}
        for user in test_data:
            with self.subTest(user=user):
                actual_result = self.table.add_setter(user).value
                self.assertEqual(actual_result, expected_result[user])
                if actual_result == 2:
                    test_cell_val = self.table.current_month_sh_r.cell(column=SETTER_COLUMN, row=test_row).value
                    pattern_test_cell_val = self.table.workbook_r['PATTERN'].cell(column=SETTER_COLUMN, row=test_row).value
                    self.assertEqual(test_cell_val, user)
                    self.assertEqual(pattern_test_cell_val, user)

                    self.table.current_month_sh_w.cell(column=SETTER_COLUMN, row=test_row).value = None
                    self.table.workbook_w['PATTERN'].cell(column=SETTER_COLUMN, row=test_row).value = None
                    self.table.workbook_w.save(self.table.tablepath)

    def test_remove_setter(self):
        test_data = ['@kraslav4ik', '@her_s_gory']
        test_row = 6
        expected_result = {'@kraslav4ik': SetterStatus.REMOVED.value, '@her_s_gory': SetterStatus.NOT_FOUND.value}
        for user in test_data:
            with self.subTest(user=user):
                actual_result = self.table.remove_setter(user).value
                self.assertEqual(actual_result, expected_result[user])
                if actual_result == 3:
                    pattern_test_cell_val = self.table.workbook_r['PATTERN'].cell(column=SETTER_COLUMN, row=test_row).value
                    self.assertEqual(pattern_test_cell_val, None)

                    self.table.workbook_w['PATTERN'].cell(column=SETTER_COLUMN, row=test_row).value = '@kraslav4ik'
                    self.table.workbook_w.save(self.table.tablepath)

    def test_add_contest(self):
        test_data = [{'date': '20.05.2022', 'name': 'jump', 'money': 500, 'amount': 1, 'result': ContestStatus.ADDED.value, 'col': FIRST_CONTEST_COL},
                     {'date': '21.05.2022', 'name': 'fly', 'money': 500, 'amount': 2, 'result': ContestStatus.ADDED.value, 'col': SECOND_CONTEST_COL},
                     {'date': '22.05.2022', 'name': 'stay', 'money': 500, 'amount': 3, 'result': ContestStatus.NO_PLACE.value}
                     ]
        for data in test_data:
            with self.subTest(data=data):
                self.assertEqual(self.table.contests, data['amount'] - 1)
                is_added = self.table.add_contest(data['date'], data['name'], data['money']).value
                self.assertEqual(is_added, data['result'])
                if data['amount'] == 3:
                    self.assertEqual(self.table.contests, data['amount'] - 1)
                    break
                price_row = 5
                name_row = 3
                self.assertEqual(self.table.contests, data['amount'])
                self.assertEqual(self.table.current_month_sh_r.cell(column=data['col'], row=price_row).value, data['money'])
                self.assertEqual(self.table.current_month_sh_r.cell(column=data['col'], row=name_row).value, data["name"])
                self.assertEqual(self.table.current_month_sh_r.cell(column=data['col'], row=DATE_ROW).value, data['date'])

            for column in (FIRST_CONTEST_COL, SECOND_CONTEST_COL):
                self.table.current_month_sh_w.cell(row=3, column=column).value = None
                self.table.current_month_sh_w.cell(row=DATE_ROW, column=column).value = None
                self.table.current_month_sh_w.cell(row=5, column=column).value = None
            self.table.workbook_w.save(self.table.tablepath)

    def test_add_contest_setter(self):
        expected_res = {'@kraslav4ik': ContestStatus.IS_CONTEST_SETTER.value, '@her_s_gory': ContestStatus.SETTER_ABSENT.value}
        test_data = [{'date': '20.05.2022', 'name': 'jump', 'money': 500, 'col': FIRST_CONTEST_COL, 'res': 'jump'},
                     {'date': '21.05.2022', 'name': 'fly', 'money': 500, 'col': SECOND_CONTEST_COL, 'res': 'jump & fly'}
                     ]
        for data in test_data:
            self.table.add_contest(data['date'], data['name'], data['money'])
            for user, result in expected_res.items():
                with self.subTest(user=user, result=result):
                    self.assertEqual(self.table.add_contest_setter(user).value, result)
                    if result == ContestStatus.IS_CONTEST_SETTER.value:
                        self.assertEqual(self.table.current_month_sh_r.cell(column=data['col'], row=11).value, data['money'])
                        self.assertEqual(self.table.current_month_sh_r.cell(column=RESULTS_COLUMN, row=11).value, data['res'])

        for column in (FIRST_CONTEST_COL, SECOND_CONTEST_COL):
            self.table.current_month_sh_w.cell(row=3, column=column).value = None
            self.table.current_month_sh_w.cell(row=DATE_ROW, column=column).value = None
            self.table.current_month_sh_w.cell(row=5, column=column).value = None
            self.table.current_month_sh_w.cell(row=11, column=column).value = None
        self.table.current_month_sh_w.cell(row=11, column=RESULTS_COLUMN).value = None
        self.table.workbook_w.save(self.table.tablepath)

    def test_remove_contest(self):
        contests = [{'date': '20.05.2022', 'name': 'jump', 'money': 500},
                    {'date': '21.05.2022', 'name': 'fly', 'money': 500}
                    ]
        setters = ['@kraslav4ik', '@ksenull']
        expected_res = [{'res': ContestStatus.REMOVED.value, 'col': SECOND_CONTEST_COL, 'names': 'jump'},
                        {'res': ContestStatus.REMOVED.value, 'col': FIRST_CONTEST_COL, 'names': None},
                        {'res': ContestStatus.NO_CONTEST.value, 'col': None}
                        ]
        for cont in contests:
            self.table.add_contest(cont['date'], cont['name'], cont['money'])
            for setter in setters:
                self.table.add_contest_setter(setter)

        for res in expected_res:
            with self.subTest(res=res):
                is_removed = self.table.remove_contest().value
                self.assertEqual(is_removed, res['res'])
                if res['col']:
                    removed_name = self.table.current_month_sh_w.cell(row=CONTEST_NAME_ROW, column=res['col']).value
                    removed_date = self.table.current_month_sh_w.cell(row=DATE_ROW, column=res['col']).value
                    removed_money = self.table.current_month_sh_w.cell(row=CONTEST_PRICE_ROW, column=res['col']).value
                    for rem in (removed_name, removed_date, removed_money):
                        self.assertEqual(rem, None)
                    rows_to_del = (11, 17)
                    for row in rows_to_del:
                        removed_res = self.table.current_month_sh_w.cell(row=row, column=RESULTS_COLUMN).value
                        removed_user_money = self.table.current_month_sh_w.cell(row=row, column=res['col']).value
                        self.assertEqual(removed_res, res['names'])
                        self.assertEqual(removed_user_money, None)

    def test_add_result(self):
        test_data = [['26.05.2022', '@kraslav4ik',  3, 3], ['26.05.2022', '@ksenull', 0, 3],
                     ['23.05.2022', '@kraslav4ik',  1, 3], ['26.05.2022', '@her',  3, 2]]
        expected_res = [ResultStatus.ADDED, ResultStatus.ADDED,
                        ResultStatus.FAIL_TO_GET_DATE, ResultStatus.NOT_SETTER]
        cells_to_rem = [(9, 10), (12, 10), (), ()]
        for data, res, cell in zip(test_data, expected_res, cells_to_rem):
            with self.subTest(data=data, res=res, cell=cell):
                self.assertEqual(self.table.add_result(*data).value, res.value)
                if res == ResultStatus.ADDED:
                    self.assertEqual(self.table.current_month_sh_r.cell(row=cell[0], column=cell[1]).value, data[3])

                    self.table.current_month_sh_w.cell(row=cell[0], column=cell[1]).value = None
                    self.table.workbook_w.save(self.table.tablepath)


def main():
    unittest.main()


if __name__ == '__main__':
    main()

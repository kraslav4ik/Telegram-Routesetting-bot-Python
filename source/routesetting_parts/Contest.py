import logging
from .Routesetting import ClimbLabSetting


class ClimbLabContest(ClimbLabSetting):

    def __init__(self, setters, contest_date, name, logger=None):
        super().__init__(setters, contest_date)
        self.contest_name = name
        self.contest_salaries = None
        self.logger = logger or logging.getLogger(__name__)

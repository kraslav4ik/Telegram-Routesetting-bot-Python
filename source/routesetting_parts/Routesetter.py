import logging


class ClimbLabRouteSetter(object):

    def __init__(self, telegram_id, boulders=None, contests=None, logger=None):
        self.telegram_id = telegram_id
        self.boulders = boulders
        self.contests = contests
        self.logger = logger or logging.getLogger(__name__)
        self.logger.info(f"Routesetter {self.telegram_id} has been added")

    def show_setter_info(self):
        pass

    def __del__(self):
        self.logger.info(f"Routesetter {self.telegram_id} has been deleted")
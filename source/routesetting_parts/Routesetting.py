from datetime import date
import logging
from typing import Dict
from .Routesetter import ClimbLabRouteSetter


class ClimbLabSetting(object):

    def __init__(self, setting_date: date, boulders: Dict[ClimbLabRouteSetter, Dict[str, int]] = None, logger=None):
        self.date = setting_date
        self.boulders = boulders if boulders else {}
        self.logger = logger or logging.getLogger(__name__)

    def show_setting_info(self):
        pass

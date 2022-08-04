from datetime import date
import logging
from typing import Dict
from .Routesetter import ClimbLabRouteSetter
from collections import defaultdict


class ClimbLabSetting(object):

    def __init__(self, setting_date: date, boulders: Dict[ClimbLabRouteSetter, Dict[str, int]] = None, logger=None):
        self.date = setting_date
        self.boulders = boulders if boulders else defaultdict(dict)
        self.logger = logger or logging.getLogger(__name__)

    def show_setting_info(self) -> dict:
        return {self.date: self.boulders.keys()}

    def __del__(self):
        self.logger.info(f"Setting {self.date} has been deleted")

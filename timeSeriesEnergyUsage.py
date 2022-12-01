
from datetime import datetime, date, timedelta
from abc import ABC, abstractmethod


class TimeSeriesEnergyUsage(ABC):

    @abstractmethod
    def process_table(self):
        pass

    @abstractmethod
    def usage_by_month(self, start: datetime, end: datetime):
        pass

    @abstractmethod
    def usage_monthly_average(self, start: datetime, end: datetime):
        pass

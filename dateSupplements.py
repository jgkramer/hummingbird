
from datetime import datetime, date, timedelta
from dateutil.rrule import rrule, MONTHLY

class DateSupplements:
    def month_starts_ends(start: datetime, end: datetime):
        monthly_starts = list(rrule(freq=MONTHLY, bymonthday = 1, dtstart=start, until=end))
        if(monthly_starts[0].date() != start.date()):
            monthly_starts = [start] + monthly_starts

        monthly_ends = list(rrule(freq=MONTHLY, bymonthday = -1, dtstart=start, until=end))
        if(monthly_ends[-1].date() != end.date()):
            monthly_ends.append(end)

        return monthly_starts, monthly_ends

    

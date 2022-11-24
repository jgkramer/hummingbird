
from datetime import datetime, date, timedelta
from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta

import pdb

class DateSupplements:
    def month_starts_ends(start: datetime, end: datetime, complete_months_only = False):
    
        month_starts = list(rrule(freq=MONTHLY, bymonthday = 1, dtstart=start, until=end))
        if(month_starts[0].date() != start.date()):
            month_starts = [start] + month_starts

        month_ends = list(rrule(freq=MONTHLY, bymonthday = -1, dtstart=start, until=end))
        if(month_ends[-1].date() != end.date()):
            month_ends.append(end)

        if complete_months_only:
           trimmed_list = [(s, e) for (s, e) in zip(month_starts, month_ends)
                           if (s.day == 1 and e == (e + relativedelta(day = 31)))]

           month_starts, month_ends = map(list, zip(*trimmed_list))

        return month_starts, month_ends

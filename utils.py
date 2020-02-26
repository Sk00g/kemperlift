import datetime
import calendar

def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year,month)[1])
    return source_date.replace(year=year, month=month, day=day)

def add_days(source_date, days):
    day = source_date.day + days
    if day > calendar.mdays[source_date.month]:
        day = 1
        return add_months(source_date.replace(day=day), 1)
    elif day < 1:
        return add_months(source_date.replace(day=calendar.mdays[source_date.month]), -1)
    else:
        return source_date.replace(day=day)
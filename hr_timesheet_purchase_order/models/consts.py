import calendar
import datetime

from dateutil.rrule import FR, MO, SA, SU, TH, TU, WE

MONTH_SELECTION = [(month.lower(), month) for month in calendar.month_name[1:]]
WEEKDAY_SELECTION = [(weekday[:3].lower(), weekday) for weekday in calendar.day_name]

current_year = datetime.datetime.now().year
DAYS_IN_MONTHS = {
    calendar.month_name[month].lower(): calendar.monthrange(current_year, month)[1]
    for month in range(1, 13)
}
WEEKS_SELECTION = [
    ("first", "First"),
    ("second", "Second"),
    ("third", "Third"),
    ("last", "Last"),
]
UNIT_SELECTION = [
    ("day", "Days"),
    ("week", "Weeks"),
    ("month", "Months"),
    ("year", "Years"),
]
DAYS = {
    "mon": MO,
    "tue": TU,
    "wed": WE,
    "thu": TH,
    "fri": FR,
    "sat": SA,
    "sun": SU,
}

TYPE_SELECTION = [
    ("forever", "Forever"),
    ("until", "End Date"),
    ("after", "Number of Repetitions"),
]

ON_MONTH_SELECTION = [
    ("date", "Date of the Month"),
    ("day", "Day of the Month"),
]

ON_YEAR_SELECTION = [
    ("date", "Date of the Year"),
    ("day", "Day of the Year"),
]

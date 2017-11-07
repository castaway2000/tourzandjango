import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
import django
django.setup()

import datetime
from guides_calendar.models import CalendarItem
import pytz


calendar_list = []
#start_time - starting time of each day for is_day_start field
def populating_hours(start, date_end):
    while start <= date_end:

        #data for Calendar model instance
        current_date = start.date()
        time_from = start
        time_to = start + datetime.timedelta(minutes=60)
        is_week_start = True if start.isoweekday() == 1 else False
        is_day_start = True if start.hour == 0 else False

        calendar_list.append(CalendarItem(date=current_date,
                                      time_from=time_from,
                                      time_to=time_to,
                                      is_week_start=is_week_start,
                                      is_day_start=is_day_start
                                      ))

        start = time_to

def populating_time_periods():
    # for testing purposes uncomment a line below

    #START ONLY with that date, which is new for prod
    start = datetime.datetime.strptime('01.11.2017 0:00:00', '%d.%m.%Y %H:%M:%S').replace(tzinfo=pytz.utc)
    date_end = datetime.datetime.strptime('30.11.2017 23:00:00', '%d.%m.%Y %H:%M:%S').replace(tzinfo=pytz.utc)
    populating_hours(start, date_end)

    # print calendar_list
    CalendarItem.objects.bulk_create(calendar_list)


if __name__ == "__main__":
    populating_time_periods()
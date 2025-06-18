import time
import calendar
from monthdelta import monthdelta
from datetime import datetime, timedelta, timezone


utc_plus_3 = timezone(timedelta(hours=3))

def get_exp_for_new_user(delta:int):
    return calendar.timegm((datetime.now() + monthdelta(delta)).timetuple())


def get_exp_time_based_on_prev(delta:int, prev_ex_time:int):
    start_time_point = datetime.fromtimestamp(
        time.mktime(time.gmtime(prev_ex_time))) if prev_ex_time is not None else datetime.now(utc_plus_3)
    return calendar.timegm((start_time_point + monthdelta(delta)).timetuple())
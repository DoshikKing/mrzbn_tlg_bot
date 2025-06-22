import time
import calendar
from monthdelta import monthdelta
from datetime import datetime

def get_exp_for_new_user(delta:int, app_timezone):
    return calendar.timegm((datetime.now(app_timezone) + monthdelta(delta)).timetuple())


def get_exp_time_based_on_prev(delta:int, prev_ex_time:int, app_timezone):
    start_time_point = datetime.fromtimestamp(
        time.mktime(time.gmtime(prev_ex_time))) if prev_ex_time is not None else datetime.now(app_timezone)
    return calendar.timegm((start_time_point + monthdelta(delta)).timetuple())
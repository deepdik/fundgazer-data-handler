import hashlib
import json

import croniter
import datetime

from api.utils.datetime_convertor import get_current_local_time


def is_required_scheduling(cron_syntax, minutes: int):
    now = get_current_local_time()
    next_schedule = now + datetime.timedelta(minutes=minutes)
    # sched = '1 15 1,15 * *'    # at 3:01pm on the 1st and 15th of every month
    if not croniter.croniter.is_valid(cron_syntax):
        print("Invalid cron syntax")
        return False, None
    print(f"next_schedule==>{next_schedule}")
    cron = croniter.croniter(cron_syntax, now)
    next = cron.get_next(datetime.datetime)
    print(f"next cron schedule==>{next}")
    if now <= next < next_schedule:
        return True, next
    return False, None

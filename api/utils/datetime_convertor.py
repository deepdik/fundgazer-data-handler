from datetime import datetime
import pytz


def convert_time(date_time: datetime):
    # get the standard UTC time
    UTC = pytz.utc

    # it will get the time zone
    # of the specified location
    IST = pytz.timezone('Asia/Kolkata')

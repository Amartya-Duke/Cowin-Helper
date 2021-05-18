import datetime
import time

TIMESTAMP_SEPARATOR = "___"
from CowinHelper.config import OTP_UTILS


def check_otp(phone_number, timeout=300):
    start_time = time.time()
    current_timestamp = datetime.datetime.now()
    while True:
        try:
            with open(OTP_UTILS['OTP_STORE_PATH'], 'r') as f:
                content = f.readline()
                if content:
                    timestamp = content.split(TIMESTAMP_SEPARATOR)[0]
                    timestamp = datetime.datetime.strptime((timestamp), "%Y/%m/%d %H:%M:%S.%f")
                    if timestamp > current_timestamp:  # we know new OTP has arrived
                        otp = content.split(TIMESTAMP_SEPARATOR)[1]
                        return otp
        except Exception as e:
            print(e)
        print("Waiting for OTP")
        if time.time() - start_time > timeout:
            print("OTP read timeout.")
            return
        time.sleep(5)  # retry after 5sec

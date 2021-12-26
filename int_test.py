import datetime
import time

start_time = datetime.datetime.now()
while 1:
    time.sleep(1)

    if (datetime.datetime.now() - start_time).total_seconds() >= 5:
        print("5 seconds passed")
        start_time = datetime.datetime.now()
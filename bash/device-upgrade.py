# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#!/usr/bin/python3

import schedule
import datetime
import time
from deviceupgradeclasses import scheduler as scheduler

schedule.every(10).seconds.do(scheduler)

while 1:
    schedule.run_pending()
    time.sleep(1)

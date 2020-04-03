# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#!/usr/bin/python3

import schedule
import datetime
import time
from trackerclasses import trackers as trackers

schedule.every(5).seconds.do(trackers)

while 1:
    schedule.run_pending()
    time.sleep(1)

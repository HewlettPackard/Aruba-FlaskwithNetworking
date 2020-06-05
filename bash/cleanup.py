# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#!/usr/bin/python3

import schedule
from datetime import date, datetime, time, timedelta
import time
from cleanupclasses import cleanupTrackers as cleanupTrackers
from cleanupclasses import cleanupLogging as cleanupLogging


schedule.every(5).seconds.do(cleanupTrackers)
schedule.every(5).seconds.do(cleanupLogging)

while 1:
    schedule.run_pending()
    time.sleep(1)

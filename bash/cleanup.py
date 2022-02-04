# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
#!/usr/bin/python3

import schedule
from datetime import date, datetime, time, timedelta
import time
from cleanupclasses import cleanupTrackers as cleanupTrackers
from cleanupclasses import cleanupafcAudit as cleanupafcAudit
from cleanupclasses import cleanupLogging as cleanupLogging
from cleanupclasses import checkSocketserver as checkSocketserver

schedule.every(5).minutes.do(cleanupTrackers)
schedule.every(5).minutes.do(cleanupLogging)
schedule.every(10).seconds.do(checkSocketserver)
schedule.every(5).minutes.do(cleanupafcAudit)

while 1:
    schedule.run_pending()
    time.sleep(1)

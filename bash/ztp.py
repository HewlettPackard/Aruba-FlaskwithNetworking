# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
#!/usr/bin/python3

import schedule
import datetime
import time
from ztpclasses import ztpupdate as ztpupdate

schedule.every(5).seconds.do(ztpupdate)

while 1:
    schedule.run_pending()
    time.sleep(1)

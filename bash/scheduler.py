# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#!/usr/bin/python3

import schedule
import datetime
import time
from jobs import trackers as trackers
from jobs import cleanup as cleanup
from jobs import ztpupdate as ztpupdate
from topology import discoverTopology as discoverTopology

schedule.every(5).seconds.do(trackers)
schedule.every(5).seconds.do(cleanup)
schedule.every(5).seconds.do(ztpupdate)
schedule.every(10).seconds.do(discoverTopology)

while 1:
    schedule.run_pending()
    time.sleep(1)

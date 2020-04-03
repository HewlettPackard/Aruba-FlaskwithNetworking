# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#!/usr/bin/python3

import schedule
import datetime
import time
from topologyclasses import discoverTopology as discoverTopology

schedule.every(10).seconds.do(discoverTopology)

while 1:
    schedule.run_pending()
    time.sleep(1)

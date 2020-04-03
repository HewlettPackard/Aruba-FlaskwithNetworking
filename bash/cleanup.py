# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#!/usr/bin/python3

import schedule
import datetime
import time
from cleanupclasses import cleanup as cleanup

schedule.every(5).seconds.do(cleanup)

while 1:
    schedule.run_pending()
    time.sleep(1)

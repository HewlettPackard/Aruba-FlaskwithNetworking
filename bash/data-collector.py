# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
#!/usr/bin/python3

import schedule
import datetime
import time
from afcdatacollectorclasses import afcvmwareinventory as afcvmwareinventory, afcintegrations as afcintegrations, afcfabrics as afcfabrics, afcswitches as afcswitches, afcauditinfo as afcauditinfo

schedule.every(5).seconds.do(afcvmwareinventory)
schedule.every(5).seconds.do(afcintegrations)
schedule.every(5).seconds.do(afcfabrics)
schedule.every(5).seconds.do(afcswitches)
schedule.every(5).seconds.do(afcauditinfo)

while 1:
    schedule.run_pending()
    time.sleep(1)
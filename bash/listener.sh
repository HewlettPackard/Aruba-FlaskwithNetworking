#!/bin/sh

activeInterface=$(route | grep '^default' | grep -o '[^ ]*$')
python3 /var/www/html/bash/listener.py $activeInterface

#rm /var/www/html/bash/trace.pcap
#touch /var/www/html/bash/trace.pcap
#tshark -i $activeInterface -c 1000 -t u -w /var/www/html/bash/trace.pcap -f "port 47 or port 67 or port 68 or port 161 or port 162 or port 514"
#/var/www/html/bash/listener.sh
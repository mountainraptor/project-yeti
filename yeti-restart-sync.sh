#!/bin/bash

ssh root@192.168.1.1 "/etc/init.d/logwifiids stop"
ssh root@192.168.1.1 "rm /mnt/usb/*"
./yeti-time.sh
ssh root@192.168.1.1 "/etc/init.d/logwifiids start"


#!/bin/bash

read -r -p "Do you want to update your time from time.nist.gov? [y,N] " response
response=${response,,}
if [[ $response =~ ^(yes|y)$ ]];
then
	sudo ntpdate -s time.nist.gov
	if [ $? -ne 0 ];
	then
		read -r -p "Do you want to update your time from time.nist.gov? [y,N] " response
		response=${response,,}
		if [[ ! $response =~ ^(yes|y)$ ]];
		then
			echo "Exiting without updating yeti time"
			exit 1
		fi
	fi
fi

DATE=$(date +%s)

ssh root@192.168.1.1 'date --set="@'$DATE'"'

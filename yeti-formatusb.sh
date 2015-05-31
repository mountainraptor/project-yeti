#!/bin/bash

if [ "$EUID" -ne 0 ];
then
	echo "We are formatting disks, you need to be root, run again as root"
	echo "Restarting with sudo"
	sudo "$0"
	exit $?
fi

lsblk

echo "Pick which device to format"
read DEVICE

read -r -p "We'll be formatting $DEVICE, are you sure? [y,N] " response
response=${response,,}
if [[ $response =~ ^(yes|y)$ ]];
then
		echo "formatting $DEVICE right meow"
else
		echo "aborting"
		exit 1
fi

MOUNT=$(mount | grep /dev/sdb | wc -l)

if  [[ $MOUNT -eq 1 ]];
then
	MOUNTED=$(mount | grep $DEVICE | cut -f 1 -d " ")
	echo "unmounting drive $MOUNTED"
	umount $MOUNTED
	if [[ $? -ne 0 ]];
	then
		echo "failed to unmount drive, aborting"
		exit 1
	fi
fi

echo -e "o\nn\np\n1\n\n\nw" | fdisk $DEVICE

if [[ $? -ne 0 ]];
then
	echo "failed to create new partition"
	exit 1
fi

$NEWPARTITION=$DEVICE"1"

mkdosfs -F 32 -n 'POTATO' -I $NEWPARTITION

#!/bin/bash

OPENWRTREMOTE="origin	git://git.openwrt.org/openwrt.git (fetch)"
REMOTE=$(git remote -v | grep fetch)

if [ "$OPENWRTREMOTE" != "$REMOTE" ];
then
	echo "Cloning OpenWRT from git://git.openwrt.org/openwrt.git to openwrt"
	git clone git://git.openwrt.org/openwrt.git openwrt
	cd openwrt

	if [ $? -ne 0 ];
	then
		echo "Failed to clone OpenWRT"
		exit 1;
	fi
else
	echo "Found OpenWRT git repo, fetching latest"
	git fetch

	if [ $? -ne 0 ];
	then
		echo "Failed to fetch latest"
		exit 1;
	fi

	git rebase

fi

git reset --hard cb8b797

echo "Updating remote feeds"

./scripts/feeds update -a

if [ $? -ne 0 ];
then
	"Failed to update feeds"
	exit 1
fi

echo "Installing feeds"

./scripts/feeds install -a

if [ $? -ne 0 ];
then
	"Failed to install new feeds"
	exit 1
fi


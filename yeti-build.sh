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

APDIR="project-yeti"

if [ ! -d "$APDIR" ];
then
	echo "Couldn't find Project Yeti Directory, cloning from githug"
	git clone https://github.com/mountainraptor/project-yeti.git project-yeti
else
	echo "Found Project Yeti directory, fetching and free basing"
	cd project-yeti
	git fetch
	git rebase
	cd ..
fi

echo "Updating mac80211.sh for default monitor mode"
cp -fpv project-yeti/openwrt-files/mac80211.sh package/kernel/mac80211/files/lib/wifi/mac80211.sh

echo "Updating shadow file"
cp -fpv project-yeti/openwrt-files/shadow package/base-files/files/etc/shadow

echo "Updating rc.local"
cp -fpv project-yeti/openwrt-files/rc.local package/base-files/files/etc/rc.local

echo "Installing secret sauce"
cp -fpv project-yeti/wifi-sniffer/logwifiids.py package/base-files/files/sbin/
cp -fpv project-yeti/wifi-sniffer/logwifiids package/base-files/files/etc/init.d/

echo "Updating make configuration"
cp -fpv project-yeti/openwrt-files/.config .

echo "Patched OpenWRT build!  Making now"

make



#!/bin/bash

pushd `dirname $0` > /dev/null
YETIDIR=`pwd`
popd > /dev/null

YETIDIRBASE=$(basename $YETIDIR)

if [ $YETIDIRBASE != 'project-yeti' ];
then
	echo "YETI: leave yeti-build.sh in it's home - project-yeti"
	exit 1
fi

git remote set-url origin git@github.com:mountainraptor/project-yeti.git

git fetch
git rebase

if [ $? -eq 1 ];
then
	git stash
	git rebase
	git stash pop
fi

if [ $? -ne 0 ];
then
	echo "YETI: failed to update yeti"
	exit 1
fi

if [ ! -d "openwrt" ];
then
	echo "YETI: could not find openwrt directory, making now"
	mkdir -p openwrt
fi

cd openwrt

OPENWRTREMOTE="origin	git://git.openwrt.org/openwrt.git (fetch)"
REMOTE=$(git remote -v | grep fetch)

if [ "$OPENWRTREMOTE" != "$REMOTE" ];
then
	echo "YETI: could not find correct remote for openwrt, clearing openwrt"
	cd ..
	rm -rf openwrt

	echo "YETI: Cloning OpenWRT from git://git.openwrt.org/openwrt.git to openwrt"
	git clone git://git.openwrt.org/openwrt.git openwrt

	if [ $? -ne 0 ];
	then
		echo "YETI: Failed to clone OpenWRT"
		exit 1;
	fi

	cd openwrt
else
	echo "YETI: Found OpenWRT git repo, fetching latest"
	git fetch

	if [ $? -ne 0 ];
	then
		echo "YETI: Failed to fetch latest"
		exit 1;
	fi

	git rebase
	
	if [ $? -ne 0 ];
	then
		git stash
		git rebase
		git stash pop
	fi
fi

git reset --hard cb8b797

echo "YETI: Updating remote feeds"

./scripts/feeds update -a

if [ $? -ne 0 ];
then
	"YETI: Failed to update feeds"
	exit 1
fi

echo "YETI: Installing feeds"

./scripts/feeds install -a

if [ $? -ne 0 ];
then
	"YETI: Failed to install new feeds"
	exit 1
fi

cd $YETIDIR
if [ $? -ne 0 ]; then
	echo "Could not change back to $YETIDIR"
	exit 1
fi

if [ ! -d "openwrt-misc" ];
then
	echo "YETI: could not find openwrt-misc directory, making now"
	mkdir -p openwrt-misc
fi

cd openwrt-misc
if [ $? -ne 0 ]; then
	echo "Could not cd to openwrt-msic"
	exit 1
fi

OPENWRTMISCREMOTE="origin	git@github.com:GBert/openwrt-misc.git (fetch)"
MISCREMOTE=$(git remote -v | grep fetch)

if [ "$OPENWRTMISCREMOTE" != "$MISCREMOTE" ];
then
	echo "YETI: could not find correct remote for openwrt-misc, clearing openwrt"
	cd ..
	rm -rf openwrt-misc

	echo "YETI: Cloning OpenWRT from git@github.com:GBert/openwrt-misc.git to openwrt-misc"
	git clone git@github.com:GBert/openwrt-misc.git

	if [ $? -ne 0 ];
	then
		echo "YETI: Failed to clone OpenWRT-misc"
		exit 1;
	fi

	cd openwrt
else
	echo "YETI: Found OpenWRT-misc git repo, fetching latest"
	git fetch

	if [ $? -ne 0 ];
	then
		echo "YETI: Failed to fetch latest"
		exit 1;
	fi

	git rebase
	
	if [ $? -ne 0 ];
	then
		git stash
		git rebase
		git stash pop
	fi
fi

cd $YETIDIR

echo "YETI: Updating mac80211.sh for default monitor mode"
cp -fpv $YETIDIR/openwrt-files/mac80211.sh $YETIDIR/openwrt/package/kernel/mac80211/files/lib/wifi/mac80211.sh

echo "YETI: Updating shadow file"
cp -fpv $YETIDIR/openwrt-files/shadow $YETIDIR/openwrt/package/base-files/files/etc/shadow

echo "YETI: Updating rc.local"
cp -fpv $YETIDIR/openwrt-files/rc.local $YETIDIR/openwrt/package/base-files/files/etc/rc.local

echo "YETI: Updating root profile to include ll"
cp -fpv $YETIDIR/openwrt-files/profile $YETIDIR/openwrt/package/base-files/files/etc/profile

echo "YETI: Installing secret sauce"
cp -fpv $YETIDIR/wifi-sniffer/logwifiids.py $YETIDIR/openwrt/package/base-files/files/sbin/
cp -fpv $YETIDIR/wifi-sniffer/logwifiids $YETIDIR/openwrt/package/base-files/files/etc/init.d/

echo "YETI: Updating make configuration"
cp -fpv $YETIDIR/openwrt-files/.config $YETIDIR/openwrt

echo "YETI: Updating GPS configurations and build"
cp -a $YETIDIR/gps/gpsd $YETIDIR/openwrt/package/network/
cp -a $YETIDIR/openwrt-misc/gpio-test $YETIDIR/openwrt/package/kernel/
cd $YETIDIR/openwrt
git checkout target/linux/ar71xx/files/arch/mips/ath79/mach-carambola2.c
patch -p1 -i $YETIDIR/gps/999-Carambola-PPS-GPIO.patch
if [ $? -ne 0 ]; then
	echo "Error applying PPS gpio pin patch"
	exit 1
fi 

echo "YETI: Patched OpenWRT build!  Making now"
cd $YETIDIR/openwrt
make

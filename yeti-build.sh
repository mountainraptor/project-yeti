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
git stash
git rebase
git stash pop

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
        rm -rf *
        cd ..

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



echo "Updating mac80211.sh for default monitor mode"
cp -fpv $YETIDIR/openwrt-files/mac80211.sh $YETIDIR/openwrt/package/kernel/mac80211/files/lib/wifi/mac80211.sh

echo "Updating shadow file"
cp -fpv $YETI_DIR/openwrt-files/shadow $YETIDIR/openwrt/package/base-files/files/etc/shadow

echo "Updating rc.local"
cp -fpv $YETIDIR/openwrt-files/rc.local $YETIDIR/openwrt/package/base-files/files/etc/rc.local

echo "Installing secret sauce"
cp -fpv $YETIDIR/wifi-sniffer/logwifiids.py $YETIDIR/openwrt/package/base-files/files/sbin/
cp -fpv $YETIDIR/wifi-sniffer/logwifiids $YETIDIR/openwrt/package/base-files/files/etc/init.d/

echo "Updating make configuration"
cp -fpv $YETIDIR/openwrt-files/.config $YETIDIR/openwrt

echo "Patched OpenWRT build!  Making now"
cd $YETIDIR/openwrt
make

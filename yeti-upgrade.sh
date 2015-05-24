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


if [ ! -d "openwrt" ];
then
	echo "YETI: could not find openwrt directory, making now"
	exit 1
fi

if [ ! -f "openwrt/bin/ar71xx/openwrt-ar71xx-generic-carambola2-squashfs-sysupgrade.bin" ];
then
	echo "YETI: could not find binary image for carambola2"
	exit 1
fi

scp "openwrt/bin/ar71xx/openwrt-ar71xx-generic-carambola2-squashfs-sysupgrade.bin" root@192.168.1.1:/tmp/
ssh root@192.168.1.1 "sysupgrade -n -v /tmp/openwrt-ar71xx-generic-carambola2-squashfs-sysupgrade.bin"

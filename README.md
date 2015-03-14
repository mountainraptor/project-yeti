# project-yeti
Probe Request Frame Tool

This project aims to put a PRF collection tool on the VoCore.  The VoCore is a small OpenWRT based embedded systems.

# Links
Build Environment: http://vocore.io/wiki/index/id:15
Uploading New Firmware: http://vocore.io/wiki/index/id:14

# Instructions
* Setup build environment
* Clone OpenWRT Source -- tested with commit hash {32509c39e4499a9060a5e76df6a0dd14dddb470c}
* Modify OpenWRT Source with specifics for VoCore & PRF Tool
** openwrt/package/base-files/files/bin/config_generate
** openwrt/package/base-files/files/etc/shadow
** openwrt/package/kernel/files/lib/wifi/mac80211.sh
** target/linux/ramips/dts/VOCORE.dts 

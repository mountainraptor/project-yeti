#
# Copyright (C) 2006-2012 OpenWrt.org
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=gpsd
PKG_VERSION:=3.10
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=http://download-mirror.savannah.gnu.org/releases/gpsd/
PKG_MD5SUM:=fc5b03aae38b9b5b6880b31924d0ace3

PKG_BUILD_DEPENDS:=libncurses libusb-1.0

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/scons.mk

define Package/gpsd/Default
  DEPENDS:=+librt
  URL:=http://catb.org/gpsd/
endef

define Package/gpsd/Default/description
  gpsd is a userland daemon acting as a translator between GPS and AIS receivers
  and their clients. gpsd listens on port 2947 for clients requesting
  position/time/velocity information.  The receivers are expected to generate
  position information in a well-known format -- as NMEA-0183 sentences, SiRF
  binary, Rockwell binary, Garmin binary format, or other vendor binary
  protocols.  gpsd takes this information from the GPS and translates it into
  something uniform and easier to understand for clients.
endef

define Package/gpsd
  $(call Package/gpsd/Default)
  SECTION:=net
  CATEGORY:=Network
  DEPENDS+= +libgps +libgpsd
  TITLE:=An interface daemon for GPS receivers
endef

define Package/gpsd/conffiles
/etc/config/gpsd
endef

define Package/gpsd/description
  $(call Package/gpsd/Default/description)
  This package contains the GPS daemon.
endef

define Package/gpsd-clients
  $(call Package/gpsd/Default)
  SECTION:=net
  CATEGORY:=Network
  DEPENDS+= +libgps +libgpsd +libncurses
  TITLE:=GPS tools and clients
endef

define Package/gpsd-clients/description
  $(call Package/gpsd/Default/description)
  This package contains auxiliary tools and example clients for monitoring and
  testing the GPS daemon.
endef

define Package/libgps
  $(call Package/gpsd/Default)
  SECTION:=libs
  CATEGORY:=Libraries
  DEPENDS+= +libcap
  TITLE:=C service library for communicating with the GPS daemon
endef

define Package/libgps/description
  $(call Package/gpsd/Default/description)
  This package contains the libgps library.
endef

define Package/libgpsd
  $(call Package/gpsd/Default)
  SECTION:=libs
  CATEGORY:=Libraries
  DEPENDS+= +libcap +libusb-1.0
  TITLE:=C service library for GPS applications
endef

define Package/libgpsd/description
  $(call Package/gpsd/Default/description)
  This package contains the libgpsd library.
endef

SCONS_OPTIONS += \
	dbus_export=no \
	tsip=no \
	fv18=no \
	tripmate=no \
	earthmate=no \
	itrax=no \
	navcom=no \
	ubx=no \
	evermore=no \
	ntrip=no \
	libgpsmm=no \
	libQgpsmm=no \
	bluez=no \
	strip=no \
	python=no \
	implicit_link=no \
	chrpath=no

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include
	$(CP) $(PKG_INSTALL_DIR)/usr/include/gps.h $(1)/usr/include/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libgps*.so* $(1)/usr/lib/
	$(INSTALL_DIR) $(1)/usr/lib/pkgconfig
	$(CP) \
		$(PKG_INSTALL_DIR)/usr/lib/pkgconfig/libgps*.pc \
		$(1)/usr/lib/pkgconfig/
endef

define Package/gpsd/install
	$(INSTALL_DIR) $(1)/etc/config
	$(INSTALL_CONF) ./files/gpsd.config $(1)/etc/config/gpsd
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/gpsd.init $(1)/etc/init.d/gpsd
	$(INSTALL_DIR) $(1)/usr/sbin
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/sbin/gpsd $(1)/usr/sbin/
endef

define Package/gpsd-clients/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/bin/cgps \
		$(PKG_INSTALL_DIR)/usr/bin/gps{ctl,decode,mon,pipe} \
		$(PKG_INSTALL_DIR)/usr/bin/gpxlogger \
		$(PKG_INSTALL_DIR)/usr/bin/lcdgps \
		$(1)/usr/bin/
endef

define Package/libgps/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libgps.so.* $(1)/usr/lib/
endef

define Package/libgpsd/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libgpsd.so.* $(1)/usr/lib/
endef

$(eval $(call BuildPackage,gpsd))
$(eval $(call BuildPackage,gpsd-clients))
$(eval $(call BuildPackage,libgps))
$(eval $(call BuildPackage,libgpsd))

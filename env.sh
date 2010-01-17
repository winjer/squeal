#!/bin/sh
virtual=`realpath virtual`
thirdparty=`realpath thirdparty`
export PATH=$virtual/bin:$PATH
export PKG_CONFIG_PATH="$thirdparty/libspotify/lib/pkgconfig"
export LD_LIBRARY_PATH="$thirdparty/libspotify/lib"
export PYTHONPATH=`realpath .`

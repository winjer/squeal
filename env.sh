#!/bin/sh
virtual=`realpath virtual`
thirdparty=`realpath thirdparty`
export PATH=$virtual/bin:$PATH
export PKG_CONFIG_PATH="$thirdparty/libspotify-0.0.2-linux6-x86/lib/pkgconfig"
export LD_LIBRARY_PATH="$thirdparty/libspotify-0.0.2-linux6-x86/lib"
export PYTHONPATH=`realpath .`

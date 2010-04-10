#!/bin/bash -x

[ $# != 1 ] && {
    echo >>/dev/stderr 'Usage: getlibspotify.sh <path to virtual environment>'
    exit 1
}

VENV=`realpath $1`

if [ `uname -m` = 'x86_64' ]
then
    wget http://developer.spotify.com/download/libspotify/libspotify-0.0.3-linux6-x86_64.tar.gz
    tar -zxf libspotify-0.0.3-linux6-x86_64.tar.gz
    rm libspotify-0.0.3-linux6-x86_64.tar.gz
    mv libspotify-0.0.3-linux6-x86_64 libspotify
else
    wget http://developer.spotify.com/download/libspotify/libspotify-0.0.3-linux6-i686.tar.gz
    tar -zxf libspotify-0.0.3-linux6-i686.tar.gz
    rm libspotify-0.0.3-linux6-i686.tar.gz
    mv libspotify-0.0.3-linux6-i686 libspotify
fi

cd libspotify

make install prefix=$VENV

echo >> $VENV/bin/activate export LD_LIBRARY_PATH=$venv/lib:$LD_LIBRARY_PATH

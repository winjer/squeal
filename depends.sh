#!/bin/bash -x

# lets use virtualenv, so we don't clobber some poor sap's computer by surprise

sudo aptitude install python python-crypto python-tagpy python-magic realpath unzip python-setuptools patch wget tar make python-tagpy

sourcedir=`realpath .`
virtualenv $sourcedir || exit 1

source ./env.sh


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
sudo make install prefix=$sourcedir
cd ..
rm -rf libspotify

easy_install formal.zip

#axiom_path=`python -c 'import axiom; print axiom.__path__[0]' 2>/dev/null`
#axiom_path=`dirname $axiom_path`
#sudo patch -d $axiom_path -p0 < patches/axiom-indexed.diff
#sudo patch -d $axiom_path -p0 < patches/axiom-indexed2.diff
#rm axiom-indexed.diff
#rm axiom-indexed2.diff

#nevow_path=`python -c 'import nevow; print nevow.__path__[0]' 2>/dev/null`
#nevow_path=`dirname $nevow_path`
#sudo patch -d $nevow_path -p0 < patches/nevow-event.diff
#rm nevow-event.diff


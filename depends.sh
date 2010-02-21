#!/bin/sh -x

sudo aptitude install python-crypto python-zopeinterface python-tagpy python-magic python-setuptools realpath python-twisted python-virtualenv python-pysqlite2 wget subversion git-arch python-imaging python-netaddr

mkdir thirdparty
cd thirdparty
svn co http://divmod.org/svn/Divmod/trunk/Nevow || exit
svn co http://divmod.org/svn/Divmod/trunk/Axiom || exit
svn co http://divmod.org/svn/Divmod/trunk/Epsilon || exit
svn co svn://pollenation.net/forms/trunk Formal || exit
git clone git://github.com/winjer/pyspotify.git || exit
if [ `uname -m` = 'x86_64' ]
then
    wget http://developer.spotify.com/download/libspotify/libspotify-0.0.3-linux6-x86_64.tar.gz
    tar -zxf libspotify-0.0.3-linux6-x86_64.tar.gz
    mv libspotify-0.0.3-linux6-x86_64 libspotify
else
    wget http://developer.spotify.com/download/libspotify/libspotify-0.0.3-linux6-i686.tar.gz
    tar -zxf libspotify-0.0.3-linux6-i686.tar.gz
    mv libspotify-0.0.3-linux6-i686 libspotify
fi
cd ..

virtualenv virtual
python pip.py install -E virtual -e thirdparty/Nevow
python pip.py install -E virtual -e thirdparty/Epsilon
python pip.py install -E virtual -e thirdparty/Axiom
python pip.py install -E virtual -e thirdparty/Formal
python pip.py install -E virtual -e thirdparty/pyspotify

patch -d thirdparty/Axiom -p0 < patches/axiom-indexed.diff
patch -d thirdparty/Axiom -p0 < patches/axiom-indexed2.diff
patch -d thirdparty/Nevow -p0 < patches/nevow-event.diff

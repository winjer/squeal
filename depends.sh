#!/bin/bash -x

sudo aptitude install python python-crypto python-tagpy python-magic realpath unzip python-setuptools patch wget tar make

py26=`python -V | grep 'Python 2.6'`
codename=`lsb_release -c`
# Python setuptools doesn't install for Python 2.6 under intrepid / hardy, neither does magic
# tagpy actually requires compiling for Py2.6 in this case.
if [ `echo $codename | egrep '(intrepid|hardy)'` && py26 ]
then
    wget http://pypi.python.org/packages/2.6/s/setuptools/setuptools-0.6c11-py2.6.egg#md5=bfa92100bd772d5a213eedd356d64086
    sudo sh setuptools-0.6c11-py2.6.egg
    rm setuptools-0.6c11-py2.6.egg
    
    magic_file=`python2.5 -c 'import magic; print magic.__file__'`
    site_packages=`python2.6 -c 'from distutils.sysconfig import get_python_lib; print get_python_lib()'`
    sudo cp $magic_file $site_packages/magic.so
    
    # now build tagpy
    wget http://pypi.python.org/packages/source/t/tagpy/tagpy-0.94.5.tar.gz
    tar -zxf tagpy-0.94.5.tar.gz
    rm tagpy-0.94.5.tar.gz
    cd tagpy-0.94.5
    # get build requirements
    sudo aptitude install libboost-dev libicu-dev libtag1-dev ctags boost-build
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib
    export INCLUDE_PATH=$INCLUDE_PATH:/usr/include/taglib
    sudo ln -sf /usr/lib/libboost_python-gcc42-mt-1_34_1.so /usr/lib/libboost_python-gcc42-mt.so
    ./configure.py
    sudo easy_install .
    cd ..
    sudo rm -rf tagpy-0.94.5
fi

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
sudo make install
cd ..
rm -rf libspotify

sudo easy_install simplejson netaddr zope.interface twisted pysqlite PIL
sudo easy_install Nevow Epsilon
sudo easy_install Axiom

wget http://forms-project.pollenation.net/cgi-bin/trac.cgi/changeset/314/trunk?format=zip\&new=314\&old=314\&new_path=trunk\&old_path=%2F -O formal.zip
unzip formal.zip -d formal
rm formal.zip
sudo easy_install formal/trunk
sudo rm -rf formal

wget http://github.com/winjer/pyspotify/tarball/master -O pyspotify.tar.gz
mkdir pyspotify
tar -zxf pyspotify.tar.gz --strip-components 1 -C pyspotify
rm pyspotify.tar.gz
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
sudo easy_install pyspotify
sudo rm -rf pyspotify

axiom_path=`python -c 'import axiom; print axiom.__path__[0]' 2>/dev/null`
axiom_path=`dirname $axiom_path`
sudo patch -d $axiom_path -p0 < patches/axiom-indexed.diff
sudo patch -d $axiom_path -p0 < patches/axiom-indexed2.diff
#rm axiom-indexed.diff
#rm axiom-indexed2.diff

nevow_path=`python -c 'import nevow; print nevow.__path__[0]' 2>/dev/null`
nevow_path=`dirname $nevow_path`
sudo patch -d $nevow_path -p0 < patches/nevow-event.diff
#rm nevow-event.diff

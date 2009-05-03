#!/bin/sh -x

sudo aptitude install python-crypto python-zopeinterface python-tagpy python-magic python-setuptools realpath python-twisted python-virtualenv

virtualenv virtual
python pip.py install -E virtual -e thirdparty/Nevow
python pip.py install -E virtual -e thirdparty/Epsilon
python pip.py install -E virtual -e thirdparty/Axiom

patch -d thirdparty/Axiom -p0 < axiom-indexed.diff
patch -d thirdparty/Axiom -p0 < axiom-indexed2.diff

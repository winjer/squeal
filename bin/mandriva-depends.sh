#!/bin/bash

su - -c "urpmi \
    python-pycrypto \
    python-tagpy \
    python-magic \
    realpath \
    make \
    libsqlite3-dev \
    python-zope-interface \
    python-twisted \
    python-imaging \
    python-virtualenv \
    python-axiom \
    python-epsilon \
    python-sqlite
"
#    python-spotify \

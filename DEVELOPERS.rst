.. -*- mode: rst ; ispell-local-dictionary: "american" -*-

================================================
How-to Setup a `squeal` Development environment
================================================

We've been round the block a few times trying to get a good developer
build of this.

I think this is so far the easiest.

Install all the packages you need. There's a script for that, select
the one for your distribution::

    ./bin/karmic-depends.sh   # for Ubuntu 9.10
    ./bin/mandriva-depends.sh # for Mandriva 2010.2

Create a virtual environment (including distribute) somewhere. Lets
call it `venv`::

    virtualenv --distribute ./venv

Activate our environment::

    source ./venv/bin/activate

Run the develop script::

    python setup.py develop

Start squeal::

    bin/squeal --database db --libpath "" fg

Now point your browser to http://localhost:9000/ .

Known problems
=================

twisted plugin cache
~~~~~~~~~~~~~~~~~~~~~

If `twisted` is not installed properly by you distribution, you will
get errors like::

  exceptions.IOError: [Errno 13] Permission denied: '/usr/lib/python2.6/site-packages/twisted/plugins/dropin.cache.new'

In this case you need to (re-) build the twisted plugin cache by
running as root::

  python -c 'import twisted.plugin as P; list(P.getPlugins(P.IPlugin))'



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

    bin/squeal --database db --libpath "" --user $USER fg

Now point your browser to http://localhost:9000/ .

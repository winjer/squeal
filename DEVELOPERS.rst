
We've been round the block a few times trying to get a good developer build of this.

I think this is so far the easiest.

Install all the packages you need.  There's a script for that::

    ./bin/karmic-depends.sh

Create a virtual environment somewhere.  Lets call it 'venv'::

    virtualenv ./venv

Install distribute::

    venv/bin/python distribute_setup.py

Activate our environment::

    source ./venv/bin/activate

Run the develop script::

    python setup.py develop

Start squeal::

    bin/start-squeal

=======================
README for Squeal 0.0.0
=======================

License
=======

Copyright 2010 Doug Winter

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Status
======

This is a work in progress that is under active development. This package is
currently of no use to you unless you are interested in contributing to
development.

Building the dependencies
=========================

In your checkout run ./depends.sh.  This works on jaunty and karmic, I have no
idea about anything else.

This will download everything you need and build it as appropriate.

You'll get a few warnings, which I have ignored safely so far.

Using the virtual environment
=============================

Then `source env.sh`

Creating the base database
==========================

./create.py

Adding a music directory (optional)
===================================

./addcoll.py /path/to/music/directory

Starting it up
==============

./start-squeal

Then point your browser to http://localhost:9000

Setting up Spotify
==================

You should now configure the spotify credentials through the web interface.  Hit the "Setup" button in the bottom right, and enter your spotify credentials in the web form.

When you submit this form, it will connect to spotify.

Connecting a SqueezeBox
=======================

Tell your player the IP address of your computer as the squeezecenter.  You
will need to /etc/init.d/apparmor stop probably, since apparmor on jaunty is
irksome.

SoftSqueeze3
============

This is the software player, which is awesome for testing.

You'll need a jre::

    sudo aptitude install sun-java6-jre

Make sure you're using the Sun JRE too, with::

    sudo update-alternatives --config java

I had to do some messing about to get actual sound out of this, which I think
is an ubuntu/jaunty/java issue.  I had to install::

    libcsnd-java

To finally make it work - but before that I'd gone through these instructions:

http://www.ubuntugeek.com/sound-solutions-for-ubuntu-904-jaunty-users.html

Which may have been also required.  Who knows.

Installing SoftSqueeze3
-----------------------

Download the rpm version without jre here:

http://sourceforge.net/project/showfiles.php?group_id=105169&package_id=113211&release_id=671140

Then convert it to a deb with::

    fakeroot alien softsqueeze_linux_3_8.rpm

This will create a deb which you can install with::

    sudo dpkg -i softsqueeze_3.8-2_i386.deb

This installs in (spit) /opt.  You can run it with::

    /opt/softsqueeze/softsqueeze

It'll spin up, and on first run will ask for your server's IP address.  Just
give it localhost.

Further Reading
===============

http://wiki.slimdevices.com/index.php?title=SlimProtoTCPProtocol


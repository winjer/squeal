================================
Developer Introduction to Squeal
================================

.. _author: Doug Winter <doug.winter@isotoma.com>

This is a brief introduction to the architecture of Squeal.  We use some pretty
esoteric stuff here that you will probably not have come across, and this
document should give you pointers to at least get a grasp on how the bits fit
together.

Software used by Squeal
=======================

Zope interfaces
---------------

The interface and adaptation system provided by zope.interface is used
extensively.  This provides a way of factoring behaviour out into loosely
coupled classes that, until you get used to it, can be quite confusing.  You
should take a look at the README_, in particular the section on Adaption.

It is very important to note that if you've used interfaces elsewhere (for
example in Java), these are NOT those interfaces.  This is something all
together different.  You are not in Kansas any more.

.. _README: http://svn.zope.org/zope.interface/trunk/src/zope/interface/README.txt?view=markup

Twisted
-------

Twisted is an event-driven networking framework, that provides an enormous
range of functionality. You will need to have a good handle on these bits:

 * `Reactor Pattern`_,
 * the concept of Deferreds_,
 * the `Component Architecture`_,
 * the `Application Framework`_ (although we're not directly using twistd),

Ultimately, if you really want to get going you should at least work through
the Howtos_ and try the programs there yourself.

.. _`Application Framework`: http://twistedmatrix.com/documents/current/core/howto/application.html
.. _`Component Architecture`: http://twistedmatrix.com/documents/current/core/howto/components.html
.. _`Reactor Pattern`: http://en.wikipedia.org/wiki/Reactor_pattern
.. _`Deferreds`: http://twistedmatrix.com/documents/current/core/howto/defer.html
.. _`Howtos`: http://twistedmatrix.com/documents/current/core/howto/

The Divmod components
---------------------

On top of Twisted we have the components from Divmod_. The Divmod programmers
overlap substantially with those of Twisted, and it uses a lot of the advanced
Twisted features.

Axiom
~~~~~

Axiom provides an object database on top of SQLite. We use Axiom to store
*everything* that we wish to persist. This includes runtime configuration, and
even which components are installed.

You should read the tutorial_, particularly the part on powerups.

.. _tutorial: http://divmod.org/trac/wiki/DivmodAxiom/Tutorial

You should be aware that when the program is run with axiomatic, what happens
is that each component in the store that provides the IService powerup is
started.

This means that if the store is empty, nothing starts up. This is what the
create.py script does - it sets up all of the appropriate IService items.

Making this work more neatly is probably a task to add to the todo list.

Nevow
~~~~~

Nevow is the web application system. Since Twisted provides so much heavy
lifting, Nevow doesn't need to do much, but it does provide a critical part
Athena_. This is the COMET_ part of the application, and we're using this to
provide all our mad leet AJAX goodness.

.. _Athena: http://divmod.org/trac/wiki/DivmodNevow/Athena
.. _COMET: http://en.wikipedia.org/wiki/Comet_(programming)

libspotify
~~~~~~~~~~

libspotify_ is provided by Spotify Ltd as a binary only object for Linux i686
and x86_64. This is clearly challenging from all sorts of perspectives, and I
hope they will see the light and distribute a proper open source version of
their code at some point. In the meantime, attempt to keep your scruples averted.

The libspotify API is very well documented at the link above. *You will need a
premium Spotify account to use this software*.

.. _libspotify: http://developer.spotify.com/en/libspotify/docs/index.html

pyspotify
~~~~~~~~~

This provides the Python interface to libspotify's shared object file. It's a
pretty straightforward implementation of the API, that has been mildly
Pythonicised.

The Squeal Architecture
=======================

The squeal architecture is componentised, using the service model from
Twisted, with each service being persisted as a powerup on the Axiom store.

These are the services that currently provide the overall application.

squeal.library.service.Library
------------------------------

Holds a number of "collections", each one of which is a

squeal.net.discovery.DiscoveryService
--------------------------------------

TBC.

squeal.playlist.service.Playlist
--------------------------------

TBC.

squeal.streaming.service.Spotify
--------------------------------

TBC.

squeal.web.service.WebService
-----------------------------

TBC.

squeal.event.EventReactor
-------------------------

TBC.

squeal.manhole.ManholeService
------------------------------

TBC.



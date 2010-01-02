THROBBER
Loading animation for jQuery
-----------------------------------------------------------

  Copyright (C) 2008 by Systemantics, Bureau for Informatics

  Lutz Issler
  Mauerstr. 10-12
  52064 Aachen
  GERMANY

  Web:    www.systemantics.net
  Email:  mail@systemantics.net

  This plugin is distributed under the terms of the
  GNU Lesser General Public license. The license can be
  obtained from http://www.gnu.org/licenses/lgpl.html.

-----------------------------------------------------------

DESCRIPTION

Throbber creates a loading animation for jQuery, ready to
be used in your AJAX applications. Of course, the throbber
is not limited to AJAX but can also be triggered manually.

DOCUMENTATION

Using the plugin is easy:

$("#button").throbber("click");

adds a loading animation (›throbber‹) to the DOM node with
the ID ›button‹ which shows up when a click event is
triggered.

The following is a list of all functions provided by the
plugin:

    * $().throbber();
      $().throbber(event);
      $().throbber(options);
      $().throbber(event, options);
      event is a string specifying the event to which the
      throbber should bind. The default here is ›click‹.
      options is a set of options (see below). Both
      parameters can be omitted
    * $.throbberShow(options);
      Immediately shows a throbber as specified. If no
      parent element is specified with options.parent, the
      throbber will be appended to the <body/> element.
    * $.throbberHide();
      Hide all throbbers.

OPTIONS

The plugin recognizes several options which are denoted in
curly brackets.

    * ajax: ›true‹ if the throbbers should listen to AJAX
      events. In this case, the throbbers are automatically
      hidden if all AJAX requests are completed. ›false‹ if
      you use AJAX, but want to hide the throbbers
      manually. Default: ›true‹
    * delay: The timeout (in milliseconds) until the
      throbber should appear. Default: ›0‹
    * image: The filename of the throbber image. Default:
      ›throbber.gif‹
    * parent: A jQuery selector specifying the parent
      element to which the throbber should be appended. All
      other child elements are automatically hidden when
      the throbber is appended. If this is left blank, the
      throbber replaces the element to which it was
      attached. Default: ›‹
    * wrap: The HTML code that should wrap the throbber.
      Default: ›‹

TIPS

If you don't use AJAX, you don't have to explicitly set the ›ajax‹
parameter to ›false‹.

The throbber element uses this HTML code:

<img src="throbber.gif" class="throbber" />

You can set wrapping code using the ›wrap‹ option.

You can create throbber images using http://www.ajaxload.info/.

EXAMPLES

    * $("#button").throbber();
      Show a throbber when the button is clicked, replacing
      the button and stopping when all AJAX requests are
      completed.
    * $("#div").throbber("dblclick", {image: "throbber_2.gif"});
      Show a throbber when #div is double-clicked, using a
      custom throbber image.

DEMONSTRATION

Have a look at demo.html, which is included in the
distribution package.

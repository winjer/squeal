/* $Id$

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
*/

// import Nevow.Athena

Squeal.W = {};

Squeal.Widget = Nevow.Athena.Widget.subclass('Squeal.Widget');

Squeal.Widget.methods(
    function __init__(self, widgetNode) {
        Squeal.Widget.upcall(self, "__init__", widgetNode);
        self.callRemote("goingLive");
        self.registerW();
    },

    function registerW(self) {
        // register with Squeal.W so other widgets can find us
    }
);


Squeal.Jukebox = Squeal.Widget.subclass("Squeal.Jukebox");
Squeal.Source = Squeal.Widget.subclass("Squeal.Source");
Squeal.Account = Squeal.Widget.subclass("Squeal.Account");
Squeal.Main = Squeal.Widget.subclass("Squeal.Main");
Squeal.Header = Squeal.Widget.subclass("Squeal.Header");
Squeal.Playlist = Squeal.Widget.subclass("Squeal.Playlist");
Squeal.Connected = Squeal.Widget.subclass("Squeal.Connected");
Squeal.Setup = Squeal.Widget.subclass("Squeal.Setup");
Squeal.PluginInstaller = Squeal.Widget.subclass("Squeal.PluginInstaller");
Squeal.PlayActions = Squeal.Widget.subclass("Squeal.PlayActions");

Squeal.PlayActions.methods(

    function registerW(self) {
        Squeal.W.playactions = self;
    },

    function play(self, node, ev) {
        self.proxy_to.play(node, ev);
    },

    function append(self, node, ev) {
        self.proxy_to.append(node, ev);
    }
);

Squeal.PluginInstaller.methods(

    function install(self, node, ev) {
        self.callRemote("install");
    }
);

Squeal.Source.methods(
    function selected(self) {
        source = self.nodeById("source").value;
        d = self.callRemote("main_widget", source);
        d.addCallback(
            function recv(le) {
                return Squeal.W.main.replaceChild(le);
            }
        );
    }
);

Squeal.Playlist.methods(
    function registerW(self) {
        Squeal.W.playlist = self;
    },

    function clear(self) {
        self.callRemote("clear");
    },

    function reload(self, data) {
        var items = data['items'];
        var current = data['current'];
        var ctr = self.nodeById("queue-items");
        ctr.innerHTML = "";
        var t = $.template('<li ${class}> \
                            <p class="track"> \
                                <span class="cover-art" style="background-image: url(${image_uri}&size=${size})"></span>\
                                <span class="track">${title}</span>\
                                <span class="artist">${artist}</span>\
                                <span class="album">${album}</span>\
                            </p>\
                            <p class="info">\
                              <a href="#" class="user">${user}</a>\
                              <span class="length">${length}</span>\
                            </p>\
                            </li>');
        _.each(items, function (p) {
            if(p.position == current) {
                p.class = 'class="current"';
                p.size = 65;
            } else {
                p.class = '';
                p.size = 50;
            }
            $(ctr).append(t, p);
        });
    }

);

Squeal.Connected.methods(
    function registerW(self) {
        Squeal.W.connected = self;
    },

    function reload(self, tag) {
        self.nodeById("connected-players").innerHTML = tag;
    },

    function setupClick(self) {
        $('.setup-pane').show(500);
    }
);

Squeal.Setup.methods(
    function registerW(self) {
        Squeal.W.setup = self;
    },

    function closeClick(self) {
        alert("closeclick");
    }

);

Squeal.Header.methods(

    function __init__(self, widgetNode) {
        Squeal.Header.upcall(self, "__init__", widgetNode);
        self.interval = null;
        self.played = 0;
        self.total = 100; // no div by zero
    },

    function reload(self, o) {
        self.nodeById("track").innerHTML = o.title;
        self.nodeById("artist").innerHTML = o.artist;
        self.nodeById("album").innerHTML = o.album;
        if(o.length) {
            self.start_progress(0, o.length);
        }
    },

    // played - the seconds played so far (0 if just starting)
    // total - the length of the track in seconds
    function start_progress(self, played, total) {
        self.played = played;
        self.total = total;
        self.display_progress();
        if(self.interval) {
            self.halt_progress();
        }
        self.interval = setInterval(_.bind(self.update_progress, self), 1000);
    },

    function update_progress(self) {
        self.played += 1000;
        self.display_progress();
    },

    function display_progress(self) {
        var percent = self.played / self.total * 100;
        var progress = self.nodeById("progress");
        $(progress).progressbar({value: percent});
        if(percent >= 100) {
            self.halt_progress();
        }
    },

    function halt_progress(self) {
        clearInterval(self.interval);
        self.interval = null;
    },

    function back(self) {
        alert("Not yet implemented: Squeal.Header.back");
    },

    function play(self) {
        alert("Not yet implemented: Squeal.Header.play");
    },

    function next(self) {
        alert("Not yet implemented: Squeal.Header.next");
    }

);

Squeal.Main.methods(
    function replaceChild(self, le) {
        var d = self.addChildWidgetFromWidgetInfo(le);
        d.addCallback(
            function childAdded(widget) {
                self.node.innerHTML = "";
                self.node.appendChild(widget.node);
            }
        );
        return d;
    },

    function registerW(self) {
        Squeal.W.main = self;
    }

);

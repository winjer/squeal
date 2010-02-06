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
Squeal.Playing = Squeal.Widget.subclass("Squeal.Playing");
Squeal.Queue = Squeal.Widget.subclass("Squeal.Queue");
Squeal.Connected = Squeal.Widget.subclass("Squeal.Connected");

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

Squeal.Queue.methods(
    function registerW(self) {
        Squeal.W.queue = self;
    },

    function clear(self) {
        self.callRemote("clear");
    },

    function reload(self, items) {
        Squeal.Foo = items;
        var ctr = self.nodeById("queue-items");
        ctr.innerHTML = "";
        for(k in items) {
            var item = items[k];
            if(item.isLoaded) {
                $(ctr).append(item['name'] + "<br/>");
            } else {
                $(ctr).append("Loading...<br/>");
            }
        }
    },

    function queueTrack(self, tid) {
        console.log("Squeal.Queue.queueTrack(" + tid + ") called")
        return self.callRemote("queueTrack", tid);
    }
);

Squeal.Connected.methods(
    function registerW(self) {
        Squeal.W.connected = self;
    },

    function reload(self, tag) {
        self.nodeById("connected-players").innerHTML = tag;
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

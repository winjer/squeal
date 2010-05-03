/*
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

Library.W = {};

Library.Widget = Nevow.Athena.Widget.subclass('Library.Widget');

Library.Widget.methods(
    function __init__(self, widgetNode) {
        Library.Widget.upcall(self, "__init__", widgetNode);
        self.callRemote("goingLive");
        self.registerW();
    },

    function registerW(self) {
        // register with Library.W so other widgets can find us
    }
);

Library.Main = Library.Widget.subclass("Library.Main");
Library.Artists = Library.Widget.subclass("Library.Artists");
Library.Albums = Library.Widget.subclass("Library.Albums");
Library.Tracks = Library.Widget.subclass("Library.Tracks");

Library.Main.methods(

    function __init__(self, widgetNode) {
        Library.Main.upcall(self, "__init__", widgetNode);
        $(widgetNode).find('li.playable').hover(
            function(){
                Squeal.W.playactions.proxy_to = self;
                $(this).append($('#play-actions'));
            },
            function(){
                $(this).find('div.actions:last').remove();
            }
        );
    },

    function play(self, node, ev) {
        var itemID = $(ev.target).parents('.playable').find("a").attr("id");
        self.callRemote("play", itemID);
    },

    function append(self, node, ev) {
        var itemID = $(ev.target).parents('.playable').find("a").attr("id");
        self.callRemote("append", itemID);
    },

    function registerW(self) {
        Library.W.main = self;
    },

    function loadAlbum(self, pid) {
        self.callRemote("load_album", pid);
    }
);

Library.Albums.methods(

    function click(self, node, ev) {
        ev.preventDefault();
        var tid = ev.target.id;
        if(tid.substring(0, 5) == "album") {
            var pid = tid.substring(6);
            Library.W.main.loadAlbum(pid);
        };
    }

);


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

Spot.W = {};

Spot.Widget = Nevow.Athena.Widget.subclass('Spot.Widget');

Spot.Widget.methods(
    function __init__(self, widgetNode) {
        Spot.Widget.upcall(self, "__init__", widgetNode);
        self.callRemote("goingLive");
        self.registerW();
    },

    function registerW(self) {
        // register with Spot.W so other widgets can find us
    }
);


Spot.Main = Spot.Widget.subclass("Spot.Main");
Spot.Playlists = Spot.Widget.subclass("Spot.Playlists");
Spot.Search = Spot.Widget.subclass("Spot.Search");

Spot.Playlists.methods(

    function registerW(self) {
        Spot.W.playlists = self;
    },

    function render(self, playlists) {
        var t = $.template('<li class="playable"><a href="#" id="playlist-${id}">${name}</a></li>');
        var ul = self.nodeById("playlists");
        $(ul).html("");
        _.each(playlists, function(p) {
            $(ul).append(t, p);
        });
        $('li.playable').hover(
            function(){
                $(this).append($('#play-actions'));
            },
            function(){
                $(this).find('div.actions:last').remove();
            }
        );
    },

    function reload(self) {
        self.callRemote("playlists").addCallback(function(x) {self.render(x);});
    }

);

Spot.Main.methods(
    function __init__(self, widgetNode) {
        Spot.Main.upcall(self, "__init__", widgetNode);
        $(self.nodeById("tab-playlists")).attr('href', "#" + $(self.nodeById("content-playlists")).attr('id'));
        $(self.nodeById("tab-search")).attr('href', "#" + $(self.nodeById("content-search")).attr('id'));
        $(self.nodeById("tabs-spotify")).tabs();
    }
);

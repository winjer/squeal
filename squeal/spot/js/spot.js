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
Spot.Search = Spot.Widget.subclass("Spot.Search");
Spot.Options = Spot.Widget.subclass("Spot.Options");
Spot.Document = Spot.Widget.subclass("Spot.Document");
Spot.Playlists = Spot.Widget.subclass("Spot.Playlists");

Spot.Playlists.methods(
    function click(self, node, ev) {
        ev.preventDefault();
        var tid = ev.target.id;
        if(tid.substring(0, 8) == "playlist") {
            var pid = tid.substring(9);
            Spot.W.document.loadPlaylist(pid);
        };
    }
)

Spot.Search.methods(
    function searchButton(self, node) {
        var field = self.nodeById("search-query");
        var query = field.value;
        self.callRemote("search", query);
    },

    function registerW(self) {
        Spot.W.search = self;
    }
);

Spot.Document.methods(
    function startThrobber(self) {
        $.throbberShow({parent: self.node,
                        image: "/static/throbber.gif",
                        ajax: false});
    },

    function registerW(self) {
        Spot.W.document = self;
    },

    function renderPlaylist(self, playlist) {
        $(self.node).html("<h1>Playlist " + pid + "</h1>");
    },

    function loadPlaylist(self, pid) {
        self.callRemote("playlist_info", int(pid)).addCallback(self.renderPlaylist);
    },

    function searchResults(self, artists, albums, tracks) {
        var t = $.template('<a href="${url}">${name}</a>, ');
        $.throbberHide();
        $(self.node).html("<h1>Search Results:</h1>");
        $(self.node).append("<h2>Artists:</h2>")
        for(k in artists) {
            $(self.node).append(t, {url: artists[k]['link'], name: artists[k]['name']})
        }
        $(self.node).append("<h2>Albums:</h2>")
        for(k in albums) {
            $(self.node).append(t, {url: albums[k]['link'], name: albums[k]['name']})
        }
        $(self.node).append("<h2>Tracks:</h2>")
        $(self.node).append('<table cellpadding="0" cellspacing="0" border="0" class="display" id="tracks-datatable"></table>')
        var trackData = [];
        for(k in tracks) {
            var t = tracks[k];
            trackData.push([t['link'], t['name'], t['album_name'], t['artist_name'], t['duration']]);
        }
        $('#tracks-datatable').dataTable({
            "aaData": trackData,
            "aoColumns": [
                {'bVisible': false},
                {'sTitle': "Track",
                  'fnRender': function(obj) {
                    return '<a href="#">' + obj.aData[1] + '</a> (<a href="javascript:Squeal.W.queue.queueTrack(\'' + obj.aData[0] + '\')">queue</a>)';
                  }},
                {'sTitle': "Album",
                  'fnRender': function(obj) {
                    return '<a href="#">' + obj.aData[2] + '</a> (<a href="#">queue</a>)';
                  }},
                {'sTitle': 'Artist',
                  'fnRender': function(obj) {
                    return '<a href="#">' + obj.aData[3] + '</a>';
                  }},
                {'sTitle': 'Time'}
            ]});
    }

);

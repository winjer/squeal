// import Nevow.Athena

 
Squeal.Widget = Nevow.Athena.Widget.subclass('Squeal.Widget');
 
Squeal.Widget.methods(
    function __init__(self, widgetNode) {
        Squeal.Widget.upcall(self, "__init__", widgetNode);
        self.callRemote("goingLive");
    }
);
 
Squeal.Jukebox = Squeal.Widget.subclass("Squeal.Jukebox");
Squeal.Source = Squeal.Widget.subclass("Squeal.Source");
Squeal.Account = Squeal.Widget.subclass("Squeal.Account");
Squeal.Search = Squeal.Widget.subclass("Squeal.Search");
Squeal.Options = Squeal.Widget.subclass("Squeal.Options");
Squeal.Main = Squeal.Widget.subclass("Squeal.Main");
Squeal.Playing = Squeal.Widget.subclass("Squeal.Playing");
Squeal.Queue = Squeal.Widget.subclass("Squeal.Queue");
Squeal.Connected = Squeal.Widget.subclass("Squeal.Connected");

Squeal.Search.methods(
    function searchButton(self, node) {
        var field = self.nodeById("search-query");
        var query = field.value;
        self.callRemote("search", query);
    }
);

Squeal.Main.methods(
    function startThrobber(self) {
        $.throbberShow({parent: self.node,
                        image: "/static/throbber.gif",
                        ajax: false});
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
            trackData.push([t['name'], t['album_name'], t['artist_name'], t['duration']]);
        }
        $('#tracks-datatable').dataTable({
            "aaData": trackData,
            "aoColumns": [
                {'sTitle': "Track",
                  'fnRender': function(obj) {
                    return '<a href="#">' + obj.aData[0] + '</a> (<a href="#">play</a>)';
                  }},
                {'sTitle': "Album",
                  'fnRender': function(obj) {
                    return '<a href="#">' + obj.aData[1] + '</a> (<a href="#">play</a>)';
                  }},
                {'sTitle': 'Artist',
                  'fnRender': function(obj) {
                    return '<a href="#">' + obj.aData[2] + '</a>';
                  }},
                {'sTitle': 'Time'}
            ]});
    }
    
);

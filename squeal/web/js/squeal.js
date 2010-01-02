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
    
    function searchResults(self, artists) {
        var t = $.template('<a href="${url}">${name}</a>, ');
        $.throbberHide();
        $(self.node).html("<h1>Search Results:</h1>");
        for(k in artists) {
            $(self.node).append(t, {url: '#', name: artists[k]['name']})
        }
    }
    
);

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

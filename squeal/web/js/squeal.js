// import Nevow.Athena

Squeal.Widget = Nevow.Athena.Widget.subclass('Squeal.Widget');

Squeal.Widget.methods(
    function __init__(self, widgetNode) {
        Squeal.Widget.upcall(self, "__init__", widgetNode);
        self.callRemote("goingLive");
    }
);

Squeal.Status = Squeal.Widget.subclass('Squeal.Status');

Squeal.Status.methods(
    function volumeChanged(self, volume) {
        var status = self.nodeById('status');
        status.innerHTML = "Volume is now " + volume;
    },

    function message(self, message) {
        var status = self.nodeById('status');
        status.innerHTML = message;
    }
);

Squeal.spotifyPlaylistRecord = Ext.data.Record.create([
    {name: 'id'},
    {name: 'name'}
]);

Squeal.SpotifyPlaylists = Squeal.Widget.subclass('Squeal.SpotifyPlaylists');

Squeal.SpotifyPlaylists.methods(
    function __init__(self, widgetNode) {
        Squeal.SpotifyPlaylists.upcall(self, "__init__", widgetNode);
        self.store = new Ext.data.Store({
            reader: Squeal.spotifyPlaylistReader
        });
        self.sm = new Ext.grid.RowSelectionModel({singleSelect: true})
        self.sm.on('rowselect', function (sm, index, record) {
            self.queue(record.get('id'));
        });
        self.reload();
        self.grid = new Ext.grid.GridPanel({
            store: self.store,
            columns: [
                {header: 'Status', width: 50, dataIndex: 'status'},
                {header: 'Name', width: 500, dataIndex: 'name'}
            ],
            viewConfig: {
                forceFit: true
            },
            sm: self.sm,
            width: 500,
            height: 600,
            frame: true,
            title: "Spotify Playlists",
            iconCls: 'icon-grid'
        });
        self.grid.render(self.nodeById('spotify-playlists'));
    },

    function load(self, data) {
        console.log(data);
        self.store.loadData(data);
    },

    function reload(self) {
        self.callRemote("reload").addCallback(function (data) {
            self.load(data);
        });
    },

    function queue(self, id) {
        self.callRemote("queue", id);
    }

);


Squeal.trackRecord = Ext.data.Record.create([
    {name: 'id'},
    {name: 'artist'},
    {name: 'album'},
    {name: 'track'},
    {name: 'title'}
]);

Squeal.playlistRecord = Ext.data.Record.create([
    {name: 'pos'},
    {name: 'id'},
    {name: 'artist'},
    {name: 'album'},
    {name: 'track'},
    {name: 'title'}
]);

Squeal.trackReader = new Ext.data.JsonReader({
    totalProperty: 'results',
    root: 'rows',
    id: 'id'
}, Squeal.trackRecord);

Squeal.playlistReader = new Ext.data.JsonReader({
    totalProperty: 'results',
    root: 'rows',
    id: 'id'
}, Squeal.playlistRecord);


Squeal.spotifyPlaylistReader = new Ext.data.JsonReader({
    totalProperty: 'results',
    root: 'rows',
    id: 'id'
}, Squeal.spotifyPlaylistRecord);

Squeal.Controls = Squeal.Widget.subclass('Squeal.Controls');

Squeal.Controls.methods(
    function __init__(self, widgetNode) {
        Squeal.Playlist.upcall(self, "__init__", widgetNode);
        self.playButton = new Ext.Button({
            text: 'Play'
        });
        self.stopButton = new Ext.Button({
            text: 'Stop'
        });
        self.playButton.on('click', self.play, self);
        self.stopButton.on('click', self.stop, self);
        var node = self.nodeById('controls');
        self.playButton.render(node);
        self.stopButton.render(node);
    },

    function play(self) {
        self.callRemote("play");
    },

    function stop(self) {
        self.callRemote("stop");
    },

    function spotify(self) {
        self.callRemote("spotify");
    }
);


Squeal.Playlist = Squeal.Widget.subclass('Squeal.Playlist');

Squeal.Playlist.methods(
    function __init__(self, widgetNode) {
        Squeal.Playlist.upcall(self, "__init__", widgetNode);
        self.store = new Ext.data.Store({
            reader: Squeal.playlistReader
        });
        self.sm = new Ext.grid.RowSelectionModel({singleSelect: true})
        self.reload();
        self.grid = new Ext.grid.GridPanel({
            store: self.store,
            columns: [
                {header: 'Position', width: 50, dataIndex: 'pos'},
                {header: 'Artist', width: 120, dataIndex: 'artist'},
                {header: 'Album', width:120, dataIndex: 'album'},
                {header: 'title', width: 120, dataIndex: 'title'}
            ],
            viewConfig: {
                forceFit: true
            },
            sm: self.sm,
            width: 1000,
            height: 300,
            frame: true,
            title: "Music",
            iconCls: 'icon-grid'
        });
        self.grid.render(self.nodeById('playlist'));
    },

    function load(self, data) {
        console.log(data);
        self.store.loadData(data);
    },

    function addTrack(self, track) {
        var data = {
            results: 1,
            rows: [track]
        };
        self.store.loadData(data, true);
    },

    function reload(self) {
        self.callRemote("reload").addCallback(function (data) {
            self.load(data);
        });
    });


Squeal.Library = Squeal.Widget.subclass('Squeal.Library');

Squeal.Library.methods(
    function __init__(self, widgetNode) {
        Squeal.Library.upcall(self, "__init__", widgetNode);
        self.store = new Ext.data.Store({
            reader: Squeal.trackReader
        });
        self.sm = new Ext.grid.RowSelectionModel({singleSelect: true})
        self.sm.on('rowselect', function (sm, index, record) {
            self.queue(record.get('id'));
        });
        self.reload();
        self.grid = new Ext.grid.GridPanel({
            store: self.store,
            columns: [
                {header: 'Artist', width: 120, dataIndex: 'artist'},
                {header: 'Album', width:120, dataIndex: 'album'},
                {header: 'title', width: 120, dataIndex: 'title'}
            ],
            viewConfig: {
                forceFit: true
            },
            sm: self.sm,
            width: 1000,
            height: 300,
            frame: true,
            title: "Music",
            iconCls: 'icon-grid'
        });
        self.grid.render(self.nodeById('library'));
    },

    function reload(self) {
        self.callRemote("reload").addCallback(function (data) {
            self.load(data);
        });
    },

    function load(self, data) {
        self.store.loadData(data);
    },

    function queue(self, id) {
        self.callRemote("queue", id);
    });

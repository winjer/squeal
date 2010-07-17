install:
	cp bin/squeal $(DESTDIR)/usr/bin/
	mkdir -p $(DESTDIR)/usr/share/squeal
	mkdir -p $(DESTDIR)/usr/share/squeal/twisted
	mkdir -p $(DESTDIR)/usr/share/squeal/twisted/plugins
	cp -r src/twisted/plugins/*.py $(DESTDIR)/usr/share/squeal/twisted/plugins/
	mkdir -p $(DESTDIR)/usr/share/squeal/formless
	mkdir -p $(DESTDIR)/usr/share/squeal/formless/test
	cp -r src/formless/*.py $(DESTDIR)/usr/share/squeal/formless/
	cp -r src/formless/test/*.py $(DESTDIR)/usr/share/squeal/formless/test/
	mkdir -p $(DESTDIR)/usr/share/squeal/epsilon
	mkdir -p $(DESTDIR)/usr/share/squeal/epsilon/hotfixes
	mkdir -p $(DESTDIR)/usr/share/squeal/epsilon/test
	mkdir -p $(DESTDIR)/usr/share/squeal/epsilon/scripts
	cp -r src/epsilon/*.py $(DESTDIR)/usr/share/squeal/epsilon/
	cp -r src/epsilon/hotfixes/*.py $(DESTDIR)/usr/share/squeal/epsilon/hotfixes/
	cp -r src/epsilon/test/*.py $(DESTDIR)/usr/share/squeal/epsilon/test/
	cp -r src/epsilon/scripts/*.py $(DESTDIR)/usr/share/squeal/epsilon/scripts/
	mkdir -p $(DESTDIR)/usr/share/squeal/axiom
	mkdir -p $(DESTDIR)/usr/share/squeal/axiom/plugins
	mkdir -p $(DESTDIR)/usr/share/squeal/axiom/scripts
	cp -r src/axiom/*.py $(DESTDIR)/usr/share/squeal/axiom/
	cp -r src/axiom/plugins/*.py $(DESTDIR)/usr/share/squeal/axiom/plugins/
	cp -r src/axiom/scripts/*.py $(DESTDIR)/usr/share/squeal/axiom/scripts/
	mkdir -p $(DESTDIR)/usr/share/squeal/formlet
	cp -r src/formlet/*.py $(DESTDIR)/usr/share/squeal/formlet/
	cp -r src/formlet/*.js $(DESTDIR)/usr/share/squeal/formlet/
	cp -r src/formlet/templates $(DESTDIR)/usr/share/squeal/formlet/
	mkdir -p $(DESTDIR)/usr/share/squeal/nevow
	mkdir -p $(DESTDIR)/usr/share/squeal/nevow/flat
	mkdir -p $(DESTDIR)/usr/share/squeal/nevow/taglibrary
	mkdir -p $(DESTDIR)/usr/share/squeal/nevow/plugins
	mkdir -p $(DESTDIR)/usr/share/squeal/nevow/scripts
	mkdir -p $(DESTDIR)/usr/share/squeal/nevow/livetrial
	cp -r src/nevow/*.py $(DESTDIR)/usr/share/squeal/nevow/
	cp -r src/nevow/css $(DESTDIR)/usr/share/squeal/nevow/
	cp -r src/nevow/flat/*.py $(DESTDIR)/usr/share/squeal/nevow/flat/
	cp -r src/nevow/taglibrary/*.py $(DESTDIR)/usr/share/squeal/nevow/taglibrary/
	cp -r src/nevow/athena_private $(DESTDIR)/usr/share/squeal/nevow/
	cp -r src/nevow/js $(DESTDIR)/usr/share/squeal/nevow/
	cp -r src/nevow/plugins/*.py $(DESTDIR)/usr/share/squeal/nevow/plugins/
	cp -r src/nevow/scripts/*.py $(DESTDIR)/usr/share/squeal/nevow/scripts/
	cp -r src/nevow/livetrial/*.py $(DESTDIR)/usr/share/squeal/nevow/livetrial/
	mkdir -p $(DESTDIR)/usr/share/squeal/squeal
	mkdir -p $(DESTDIR)/usr/share/squeal/squeal/playlist
	mkdir -p $(DESTDIR)/usr/share/squeal/squeal/web
	mkdir -p $(DESTDIR)/usr/share/squeal/squeal/spot
	mkdir -p $(DESTDIR)/usr/share/squeal/squeal/player
	mkdir -p $(DESTDIR)/usr/share/squeal/squeal/test
	mkdir -p $(DESTDIR)/usr/share/squeal/squeal/library
	mkdir -p $(DESTDIR)/usr/share/squeal/squeal/library/tests
	mkdir -p $(DESTDIR)/usr/share/squeal/squeal/net
	mkdir -p $(DESTDIR)/usr/share/squeal/squeal/plugins
	cp -r src/squeal/*.py $(DESTDIR)/usr/share/squeal/squeal/
	cp -r src/squeal/playlist/*.py $(DESTDIR)/usr/share/squeal/squeal/playlist/
	cp -r src/squeal/web/*.py $(DESTDIR)/usr/share/squeal/squeal/web/
	cp -r src/squeal/web/static $(DESTDIR)/usr/share/squeal/squeal/web/
	cp -r src/squeal/web/js $(DESTDIR)/usr/share/squeal/squeal/web/
	cp -r src/squeal/web/templates $(DESTDIR)/usr/share/squeal/squeal/web/
	cp -r src/squeal/spot/*.py $(DESTDIR)/usr/share/squeal/squeal/spot/
	cp -r src/squeal/spot/appkey.key $(DESTDIR)/usr/share/squeal/squeal/spot/
	cp -r src/squeal/spot/js $(DESTDIR)/usr/share/squeal/squeal/spot/
	cp -r src/squeal/spot/templates $(DESTDIR)/usr/share/squeal/squeal/spot/
	cp -r src/squeal/player/*.py $(DESTDIR)/usr/share/squeal/squeal/player/
	cp -r src/squeal/player/font $(DESTDIR)/usr/share/squeal/squeal/player
	cp -r src/squeal/test/*.py $(DESTDIR)/usr/share/squeal/squeal/test/
	cp -r src/squeal/library/*.py $(DESTDIR)/usr/share/squeal/squeal/library/
	cp -r src/squeal/library/js $(DESTDIR)/usr/share/squeal/squeal/library/
	cp -r src/squeal/library/templates $(DESTDIR)/usr/share/squeal/squeal/library/
	cp -r src/squeal/library/tests/*.py $(DESTDIR)/usr/share/squeal/squeal/library/tests/
	cp -r src/squeal/library/tests/files $(DESTDIR)/usr/share/squeal/squeal/library/tests/
	cp -r src/squeal/net/*.py $(DESTDIR)/usr/share/squeal/squeal/net/
	cp -r src/squeal/plugins/*.py $(DESTDIR)/usr/share/squeal/squeal/plugins/


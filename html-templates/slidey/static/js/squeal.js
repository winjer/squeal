$(function() {
    $('#controls-back').button({
        text: false,
        icons: { primary: 'ui-icon-seek-start' }
    });
    
    $('#controls-play').button({
        text: false,
        icons: { primary: 'ui-icon-play' }
    }).click(function() {
        var options;
        if ($(this).text() == 'Play') {
            options = { label: 'Stop', icons: { primary: 'ui-icon-stop' } };
        } else {
            options = { label: 'Play', icons: { primary: 'ui-icon-play' } };
        }
        $(this).button('option', options);
    });
    
    $('#controls-next').button({
        text: false,
        icons: { primary: 'ui-icon-seek-end' }
    });

    $('#sources').accordion({
		icons: false,
		autoHeight: false,
		active: 1
	});
	
    $('#playlist').accordion({ 
        icons: false, 
        autoHeight: false 
    });

	$("#progress").progressbar({
		value: 33
	});

	$('#volume').slider({
		value: 75,
		min: 0,
		max: 100});

	$('#main div.panel dl dd ul li').hover(
		function(){
			$(this).append($('#play-actions'));
		},
		function(){
			$(this).find('div.actions:last').remove();
		}
	);
	
	$('#main div.panel dl dt').click(function(){
		if($(this).next().is(':visible')) {
		    $(this).next().hide();
    	    $(this).find('span.toggle').text('[+]');
		}
		else {
		    $(this).next().show();
    	    $(this).find('span.toggle').text('[-]');
		}
	});
	
	$('#main div.panel dl dt').each(function(){
	    $(this).next().toggle();
	    $(this).prepend('<span class="toggle">[+]</span>');
	});

	$("#tabs-spotify").tabs({
		selected: 1
	});
});

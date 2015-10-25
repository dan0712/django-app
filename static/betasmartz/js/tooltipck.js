/**
 * copyright	Copyright (C) 2010 Cedric KEIFLIN alias ced1870 & Ghazal
 * http://www.joomlack.fr
 * license		GNU/GPL
 * Tooltip GC
 **/

(function($) {
	$.fn.Tooltipck = function(options) {
		var defaults = {
			fxtransition: 'linear',
			fxduration: 500,
			dureeIn: 0,
			dureeBulle: 500,
			// largeur : '150',
			ismobile: 0,
			opacite: 0.8
			// offsetx: '0',
			// offsety: '0'
			// dureebulle : 500
		};
		var options = $.extend(defaults, options);
		var tooltip = this;

		$('.infotip').each(function(i, tooltip) {
			tooltip = $(tooltip);
			tooltip.tip = $('> .tooltipck_tooltip', tooltip);
			tooltip.width = tooltip.tip.width();
			tooltip.height = tooltip.tip.height();
			tooltip.tip.css({
					'opacity': '0',
					'width': '0',
					'height': '0',
				});
			getTooltipParams(tooltip);
			if (options.ismobile === 1) {
				tooltip.click(function() {
					if (tooltip.data('status') != 'open') {
						showTip(tooltip);
					} else {
						hideTip(tooltip);
					}
				});
			} else {
				tooltip.mouseover(function() {
					showTip(tooltip);
				});
				tooltip.mouseleave(function() {
					hideTip(tooltip);
				});
			}

			function showTip(el) {
				clearTimeout(el.timeout);
				el.timeout = setTimeout(function() {
					openTip(el);
				}, options.dureeIn);
			}

			function hideTip(el) {
				$(el).data('status', 'hide')
				clearTimeout(el.timeout);
				el.timeout = setTimeout(function() {
					closeTip(el);
				}, tooltip.dureeBulle);
			}

			function openTip(el) {
				tip = $(el.tip);
				el.data('status', 'open');
				if (el.data('status') == 'opened')
					return;
				tip.animate({
					'opacity' : options.opacite,
					'height' : el.height,
					'width' : el.width,
					'display' : 'inline-block'
					}, parseInt(tooltip.fxduration), options.fxtransition, {
					complete: function() {
						el.data('status', 'opened');
						tip.css('height' ,'auto');
					}
				});
			}

			function closeTip(el) {
				tip = $(el.tip);
				el.data('status', 'close');
				tip.stop(true, true);
				tip.css({
					'opacity': '0',
					'width': '0',
					'height': '0',
					'display' : 'none'
				});
				el.data('status', 'closed');
			}

			function getTooltipParams(tooltip) {
				if (tooltip.attr('rel').length) {
					var params = tooltip.attr('rel').split('|');
					for (var i = 0; i < params.length; i++) {
						param = params[i];
//                    params.each( function(param) {
						// if (param.indexOf('w=') != -1) largeur = param.replace("w=", "");
						if (param.indexOf('mood=') != -1)
							tooltip.fxduration = param.replace("mood=", "");
						if (param.indexOf('tipd=') != -1)
							tooltip.dureeBulle = param.replace("tipd=", "");
						if (param.indexOf('offsetx=') != -1)
							tooltip.offsetx = parseInt(param.replace("offsetx=", ""));
						if (param.indexOf('offsety=') != -1)
							tooltip.offsety = parseInt(param.replace("offsety=", ""));
//                    });
					}

					$(tooltip.tip).css({
						// 'opacity': options.opacite,
						'marginTop': tooltip.offsety,
						'marginLeft': tooltip.offsetx
					});
				}
			}
		});
	}
})(jQuery);
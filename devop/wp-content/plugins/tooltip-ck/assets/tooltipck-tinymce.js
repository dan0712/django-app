(function() {
	tinymce.create('tinymce.plugins.tooltipck', {
		init : function(ed, url) {
			ed.addButton('tooltipck', {
				title : 'Tooltip CK',
				image : url+'/tooltipckmcebutton.png',
				onclick : function() {
					myform = jQuery('<div title="Create your Tooltip CK" ></div>');
					if (window.tooltipck_cache) {
						myform.html(window.tooltipck_cache);
					} else {
						jQuery.get(url+'/ajax_editorbuttonform.html', function(data) {
							window.tooltipck_cache = data;
							myform.html(window.tooltipck_cache);
						});
					}
					myform.dialog({
						autoOpen: true,
						draggable: false,
						resizable: false,
						modal: true,
						dialogClass: 'wp-dialog',
						close: function( event, ui ) {
							jQuery(this).dialog( "destroy" );
							jQuery(this).remove();
						},
						buttons: {
							"Insert": function() {
								var ckform = jQuery("#tooltipck_button_form");
								tooltipck_text = jQuery("#tooltipck_text").val();
								tooltipck_tip = jQuery("#tooltipck_tip").val();
								var tooltipck_params = Array();
								jQuery('.tooltipck_param', ckform).each(function(i, param) {
									if (jQuery(param).val())
										tooltipck_params.push(jQuery(param).attr('data-param')+'='+jQuery(param).val());
								});
								if (tooltipck_params.length) {
									tooltipck_midtag = '{end-texte|' + tooltipck_params.join('|') + '}';
								} else {
									tooltipck_midtag = '{end-texte}';
								}
								if (tooltipck_text != null && tooltipck_text != '' && tooltipck_tip != null && tooltipck_tip != ''){
									ed.execCommand('mceInsertContent', false, '{tooltip}'+tooltipck_text+tooltipck_midtag+tooltipck_tip+'{end-tooltip}');
								}
								jQuery(this).dialog( "destroy" );
								jQuery(this).empty();
							},
							Cancel: function() {
								jQuery(this).dialog( "destroy" );
								jQuery(this).empty();
							}
						}
					});
				}
			});
		}
	});
	tinymce.PluginManager.add('tooltipck', tinymce.plugins.tooltipck);
})();
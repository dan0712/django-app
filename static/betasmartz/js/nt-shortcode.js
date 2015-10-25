jQuery(document).ready(function($) {

// Box
$('.nt-box .nt-icon-cancel-circled').click(function(){
	$(this).parent('.nt-box').fadeOut('fast');
});

// Tab
$('.nt-nt_tabs-wrap').each(function(){
	var tab_group = $(this);
	$('.nt_tabs li', tab_group).click(function(e){
		e.preventDefault();
		$('.nt_tabs li', tab_group).removeClass('current');
		$(this).addClass('current');

		$('.panes .pane', tab_group).hide();
		$('.panes .pane', tab_group).eq($(this).index()).show();
	});

	// Trigger Initial Tab
	var initial_tab = parseInt( $('.nt_tabs', this).data('active') );
	$('.nt_tabs li', tab_group).eq(initial_tab).trigger('click');
});

// Accordion
$('.nt-nt_accordions-wrap').each(function(){
	var acc_group = $(this);
	$('.tab', acc_group).click(function(){
		$('.tab', acc_group).not($(this)).removeClass('current');
		$(this).addClass('current');
		$(this).next('.pane').slideDown(200, 'linear');
		$('.pane', acc_group).not($(this).next('.pane')).slideUp(200, 'linear');
	});

	// Trigger Initial Tab
	var initial_tab = parseInt( $(this).data('active') );
	$('.tab', acc_group).eq(initial_tab).addClass('current').next('.pane').show();
});

// Toggle
$('.nt-toggle-wrap .tab').click(function(){
	$(this).toggleClass('current');
	$(this).siblings('.pane').slideToggle(200, 'linear');
});
$('.nt-toggle-wrap').each(function(){
	if( $(this).data('state') == 'open' ) {
		$('.pane', $(this)).show();
	}
});
	
	
});
<?php

require_once( 'settings-api.class.php' );
require_once( 'settings.config.php' );
require_once( 'settings.menu.php' );

/* Add Settings Link to Plugins Panel */
function shiftnav_plugin_settings_link( $links ) {
	$settings_link = '<a href="'.admin_url( 'themes.php?page=shiftnav-settings' ).'">Settings</a>';
	array_unshift( $links, $settings_link );
	return $links;
}
add_filter( 'plugin_action_links_'.SHIFTNAV_BASENAME, 'shiftnav_plugin_settings_link' );


function shiftnav_pro_link(){
	?>
	<div class="shiftnav_pro_button_container">
		<a target="_blank" href="http://goo.gl/rd12PP" class="shiftnav_pro_button"><i class="fa fa-rocket"></i> Go Pro</a>
	</div>
	<?php
}
if( !SHIFTNAV_PRO ) add_action( 'shiftnav_settings_before' , 'shiftnav_pro_link' );
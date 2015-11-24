<?php

function shiftnav_settings_links(){
	echo '<a target="_blank" class="button button-primary" href="http://sevenspark.com/docs/shiftnav"><i class="fa fa-book"></i> Knowledgebase</a> ';
}
add_action( 'shiftnav_settings_before_title' , 'shiftnav_settings_links' );

function shiftnav_get_settings_fields(){

	$prefix = SHIFTNAV_PREFIX;


	$main_assigned = '';
	if(!has_nav_menu('shiftnav')){
		$main_assigned = 'No Menu Assigned';
	}
	else{
    	$menus = get_nav_menu_locations();
    	$menu_title = wp_get_nav_menu_object($menus['shiftnav'])->name;
    	$main_assigned = $menu_title;
    }

    $main_assigned = '<span class="shiftnav-main-assigned">'.$main_assigned.'</span>  <p class="shiftnav-desc-understated">The menu assigned to the <strong>ShiftNav [Main]</strong> theme location will be displayed.  <a href="'.admin_url( 'nav-menus.php?action=locations' ).'">Assign a menu</a></p>';
	


	$fields = array(
		

		$prefix.'shiftnav-main' => array(

			array(
				'name'	=> 'menu_assignment',
				'label'	=> __( 'Assigned Menu' , 'shiftnav' ),
				'desc'	=> $main_assigned,
				'type'	=> 'html',

			),

			array(
				'name' => 'display_main',
				'label' => __( 'Display Main ShiftNav', 'shiftnav' ),
				'desc' => __( 'Do not uncheck this unless you want to disable the main ShiftNav panel entirely.', 'shiftnav' ),
				'type' => 'checkbox',
				'default' => 'on'
			),

			array(
				'name'		=> 'edge',
				'label'		=> __( 'Edge' , 'shiftnav' ),
				'type'		=> 'radio',
				'options' 	=> array(
					'left' 	=> 'Left',
					'right'	=> 'Right',
				),
				'default' 	=> 'left'
			),

			array(
				'name' => 'swipe_open',
				'label' => __( 'Swipe Open', 'shiftnav' ),
				'desc' => __( 'Swipe to open the main ShiftNav Panel in iOS and Android.  Not all themes will be compatible, as touch swipes can conflict with theme scripts.  Make sure enabling this doesn\'t prevent other touch functionality on your site from working', 'shiftnav' ),
				'type' => 'checkbox',
				'default' => 'off'
			),

			array(
				'name'	=> 'skin',
				'label'	=> __( 'Skin' , 'shiftnav' ),
				'type'	=> 'select',
				'options' => shiftnav_get_skin_ops(),
				'default' => 'standard-dark',
				//'options' => get_registered_nav_menus()
			),

			array(
				'name'		=> 'indent_submenus',
				'label'		=> __( 'Indent Always Visible Submenus' , 'shiftnav' ),
				'desc'		=> __( 'Check this to indent submenu items of always-visible submenus' , 'shiftnav' ),
				'type'		=> 'checkbox',
				'default'	=> 'off',
			),

			array(
				'name' => 'display_site_title',
				'label' => __( 'Display Site Title', 'shiftnav' ),
				'desc' => __( 'Display the site title in the menu', 'shiftnav' ),
				'type' => 'checkbox',
				'default' => 'on'
			),




			/*
			array(
				'name' => 'inherit_ubermenu_icons',
				'label' => __( 'Inherit UberMenu Icons', 'shiftnav' ),
				'desc' => __( 'Display the icon from the UberMenu icon setting if no icon is selected', 'shiftnav' ),
				'type' => 'checkbox',
				'default' => 'off'
			),
			*/

		),
			// array( 
			// 	'name'	=> 'section_toggle',
			// 	'label'	=> '<h4 class="shiftnav-settings-section">'.__( 'Top Bar Toggle Settings' , 'shiftnav' ).'</h4>',
			// 	'desc'	=> '<span class="shiftnav-desc-understated">'.__( 'These settings control the main ShiftNav toggle' , 'shiftnav' ).'</span>',
			// 	'type'	=> 'html',
			// ),


		$prefix.'togglebar' => array(
			array(
				'name' => 'display_toggle',
				'label' => __( 'Display Toggle Bar', 'shiftnav' ),
				'desc' => __( '', 'shiftnav' ),
				'type' => 'checkbox',
				'default' => 'on'
			),
			array(
				'name' => 'breakpoint',
				'label' => __( 'Toggle Breakpoint', 'shiftnav' ),
				'desc' => __( 'Show the toggle bar only below this pixel width.  Leave blank to show at all times.  Do not include "px"', 'shiftnav' ),
				'type' => 'text',
				'default' => ''
			),
			array(
				'name' => 'hide_theme_menu',
				'label' => __( 'Hide Theme Menu', 'shiftnav' ),
				'desc' => __( 'Enter the selector of the theme\'s menu if you wish to hide it below the breakpoint above.  For example, <code>#primary-nav</code> or <code>.topnav</code>.  ', 'shiftnav' ),
				'type' => 'text',
				'default' => ''
			),
			array(
				'name' => 'hide_ubermenu',
				'label' => __( 'Hide UberMenu', 'shiftnav' ),
				'desc' => __( 'Hide all UberMenus when ShiftNav is displayed.  If you would like to only hide a specific UberMenu, use the setting above with a specific UberMenu ID.', 'shiftnav' ) . ' ( <a href="http://wpmegamenu.com">What is UberMenu?</a> )',
				'type' => 'checkbox',
				'default' => 'off'
			),
			array(
				'name'	=> 'toggle_content',
				'label'	=> __( 'Toggle Content' , 'shiftnav' ),
				'desc'	=> __( '[shift_toggle_title]' , 'shiftnav' ),
				'type'	=> 'textarea',
				'default' => '[shift_toggle_title]', //get_bloginfo( 'title' )
				'sanitize_callback' => 'shiftnav_allow_html',
			),



			array(
				'name'	=> 'toggle_close_icon',
				'label' => __( 'Close Icon' , 'shiftnav' ),
				'desc'	=> __( 'When the toggle is open, choose which icon to display.', 'shiftnav' ),
				'type'	=> 'radio',
				'options' => array(
					'bars'	=> '<i class="fa fa-bars"></i> Hamburger Bars',
					'x'		=> '<i class="fa fa-times"></i> Close button',
				),
				'default' => 'x',
			),
			array(
				'name'	=> 'toggle_position',
				'label' => __( 'Toggle Bar Position' , 'shiftnav' ),
				'desc'	=> __( 'Choose Fixed if you\'d like the toggle bar to always be visible, or Absolute if you\'d like it only to be visible when scrolled to the very top of the page', 'shiftnav' ),
				'type'	=> 'radio',
				'options' => array(
					'fixed'		=> __( 'Fixed', 'shiftnav' ),
					'absolute'	=> __( 'Absolute' , 'shiftnav' ),
				),
				'default' => 'fixed',
			),

			array(
				'name'	=> 'align',
				'label' => __( 'Align Text' , 'shiftnav' ),
				'desc'	=> __( 'Align text left, right, or center.  Applies to inline elements only.', 'shiftnav' ),
				'type'	=> 'radio',
				'options' => array(
					'center'=> 'Center',
					'left'	=> 'Left',
					'right'	=> 'Right',
				),
				'default' => 'center',
			),

			array(
				'name'	=> 'background_color',
				'label'	=> __( 'Background Color' , 'shiftnav' ),
				'desc'	=> __( '' , 'shiftnav' ),
				'type'	=> 'color',
				//'default' => '#1D1D20',
			),

			array(
				'name'	=> 'text_color',
				'label'	=> __( 'Text Color' , 'shiftnav' ),
				'desc'	=> __( '' , 'shiftnav' ),
				'type'	=> 'color',
				//'default' => '#eeeeee',
			),

			array(
				'name' => 'font_size',
				'label' => __( 'Font Size', 'shiftnav' ),
				'desc' => __( 'Override the default font size of the toggle bar by setting a value here.', 'shiftnav' ),
				'type' => 'text',
				'default' => ''
			),
			

			/*
			array(
				'name' => 'display_condition',
				'label' => __( 'Display on', 'shiftnav' ),
				'desc' => __( '', 'shiftnav' ),
				'type' => 'multicheck',
				'options' => array(
					'all' 	=> 'All',
					'posts' => 'Posts',
					'pages' => 'Pages',
					'home' 	=> 'Home Page',
					'blog'	=> 'Blog Page',
				),
				'default' => array( 'all' => 'all' )
			),
			*/
			
		),
		
	);
	
	$fields = apply_filters( 'shiftnav_settings_panel_fields' , $fields );

	$fields[$prefix.'general'] = array(
		
		array( 
			'name'	=> 'css_tweaks',
			'label'	=> __( 'CSS Tweaks' , 'shiftnav' ),
			'desc'	=> __( 'Add custom CSS here, which will be printed in the site head.' , 'shiftnav' ),
			'type'	=> 'textarea',
			'sanitize_callback' => 'shiftnav_allow_html',
		),

		array(
			'name' => 'target_size',
			'label' => __( 'Button Size', 'shiftnav' ),
			'desc' => __( 'The size of the padding on the links in the menu.  The larger the setting, the easier to click; but fewer menu items will appear on the screen at a time.', 'shiftnav' ),
			'type' => 'radio',
			'options' => array(
				'default' 	=> 'Default',
				'medium' 	=> 'Medium',
				'large'		=> 'Large',
				'enormous' 	=> 'Enormous',
			),
			'default' => 'default',
		),

		array(
			'name' => 'text_size',
			'label' => __( 'Text Size', 'shiftnav' ),
			'desc' => __( 'The size of the font on the links in the menu (will override all levels).', 'shiftnav' ),
			'type' => 'radio',
			'options' => array(
				'default' 	=> 'Default',
				'small'		=> 'Small',
				'medium' 	=> 'Medium',
				'large'		=> 'Large',
				'enormous' 	=> 'Enormous',
			),
			'default' => 'default',
		),

		array(
			'name' => 'icon_size',
			'label' => __( 'Icon Size', 'shiftnav' ),
			'desc' => __( 'The size of the icons in the menu.', 'shiftnav' ),
			'type' => 'radio',
			'options' => array(
				'default' 	=> 'Default',
				'small'		=> 'Small',
				'medium' 	=> 'Medium',
				'large'		=> 'Large',
				'enormous' 	=> 'Enormous',
			),
			'default' => 'default',
		),

		array(
			'name' 		=> 'shift_body',
			'label' 	=> __( 'Shift Body', 'shiftnav' ),
			'desc' 		=> __( 'Shift the body of the site when the menu is revealed.  For some themes, this may negatively affect the site content, so this can be disabled.', 'shiftnav' ),
			'type' 		=> 'checkbox',
			'default' 	=> 'on'
		),

		array(
			'name' 		=> 'swipe_close',
			'label' 	=> __( 'Swipe Close', 'shiftnav' ),
			'desc' 		=> __( 'Enable swiping to close the ShiftNav panel on Android and iOS.  Touch events may not interact well with all themes.', 'shiftnav' ),
			'type' 		=> 'checkbox',
			'default' 	=> 'on'
		),

		array(
			'name' 		=> 'swipe_tolerance_x',
			'label' 	=> __( 'Swipe Tolerance: Horizontal', 'shiftnav' ),
			'desc' 		=> __( 'The minimum horizontal pixel distance before the swipe is triggered.  Do not include <code>px</code>', 'shiftnav' ),
			'type' 		=> 'text',
			'default' 	=> 150
		),

		array(
			'name' 		=> 'swipe_tolerance_y',
			'label' 	=> __( 'Swipe Tolerance: Vertical', 'shiftnav' ),
			'desc' 		=> __( 'The maximum horizontal pixel distance allowed for the swipe to be triggered.  Do not include <code>px</code>', 'shiftnav' ),
			'type' 		=> 'text',
			'default' 	=> 60
		),

		array(
			'name' 		=> 'swipe_edge_proximity',
			'label' 	=> __( 'Swipe Edge Proximity', 'shiftnav' ),
			'desc' 		=> __( 'The distance from the edge, within which the first touch event must occur for the swipe to be triggered.  Do not include <code>px</code>', 'shiftnav' ),
			'type' 		=> 'text',
			'default' 	=> 80
		),

		array(
			'name' 		=> 'open_current',
			'label' 	=> __( 'Open Current Accordion Submenu', 'shiftnav' ),
			'desc' 		=> __( 'Open the submenu of the current menu item on page load (accordion submenus only).', 'shiftnav' ),
			'type' 		=> 'checkbox',
			'default' 	=> 'off'
		),	

		array(
			'name' 		=> 'collapse_accordions',
			'label' 	=> __( 'Collapse Accordions', 'shiftnav' ),
			'desc' 		=> __( 'When an accordion menu is opened, collapse any other accordions on that level.', 'shiftnav' ),
			'type' 		=> 'checkbox',
			'default' 	=> 'off'
		),

		array(
			'name' 		=> 'scroll_panel',
			'label' 	=> __( 'Scroll Shift Submenus to Top', 'shiftnav' ),
			'desc' 		=> __( 'When a Shift submenu is activated, scroll that item to the top to maximize submenu visibility.', 'shiftnav' ),
			'type' 		=> 'checkbox',
			'default' 	=> 'on'
		),
		

		array(
			'name' 		=> 'active_on_hover',
			'label' 	=> __( 'Highlight Targets on Hover', 'shiftnav' ),
			'desc' 		=> __( 'With this setting enabled, the links will be highlighted when hovered or touched.', 'shiftnav' ),
			'type' 		=> 'checkbox',
			'default' 	=> 'off'
		),

		array(
			'name' 		=> 'active_highlight',
			'label' 	=> __( 'Highlight Targets on :active', 'shiftnav' ),
			'desc' 		=> __( 'With this setting enabled, the links will be highlighted while in the :active state.  May not be desirable for touch scrolling.', 'shiftnav' ),
			'type' 		=> 'checkbox',
			'default' 	=> 'off'
		),
		
		array(
			'name' 		=> 'admin_tips',
			'label' 	=> __( 'Show Tips to Admins', 'shiftnav' ),
			'desc' 		=> __( 'Display tips to admin users', 'shiftnav' ),
			'type' 		=> 'checkbox',
			'default' 	=> 'on'
		),

		array(
			'name' 		=> 'lock_body_x',
			'label' 	=> __( 'Lock Horizontal Scroll', 'shiftnav' ),
			'desc' 		=> __( 'Attempt to prevent the content from scrolling horizontally when the menu is active.  On some themes, may also prevent vertical scrolling.  May not prevent touch scrolling in Chrome.  No effect if <strong>Shift Body</strong> is disabled.', 'shiftnav' ),
			'type' 		=> 'checkbox',
			'default' 	=> 'off'
		),

		array(
			'name' 		=> 'lock_body',
			'label' 	=> __( 'Lock Scroll', 'shiftnav' ),
			'desc' 		=> __( 'Lock both vertical and horizontal scrolling on site content when menu is active.  No effect if <strong>Shift Body</strong> is disabled.', 'shiftnav' ),
			'type' 		=> 'checkbox',
			'default' 	=> 'on'
		),

		array(
			'name' 		=> 'load_fontawesome',
			'label' 	=> __( 'Load Font Awesome', 'shiftnav' ),
			'desc' 		=> __( 'If you are already loading Font Awesome 4 elsewhere in your setup, you can disable this.', 'shiftnav' ),
			'type' 		=> 'checkbox',
			'default' 	=> 'on'
		),

		array(
			'name' => 'inherit_ubermenu_conditionals',
			'label' => __( 'Inherit UberMenu Conditionals', 'shiftnav' ),
			'desc' => __( 'Display menu items based on UberMenu Conditionals settings', 'shiftnav' ),
			'type' => 'checkbox',
			'default' => 'off'
		),

		array(
			'name' 		=> 'force_filter',
			'label' 	=> __( 'Force Filter Menu Args', 'shiftnav' ),
			'desc' 		=> __( 'Some themes will filter the menu arguments on all menus on the site, which can break things.  This will re-filter those arguments for ShiftNav menus only.', 'shiftnav' ),
			'type' 		=> 'checkbox',
			'default' 	=> 'off'
		),

		array(
			'name' 		=> 'kill_class_filter',
			'label' 	=> __( 'Kill Menu Class Filter', 'shiftnav' ),
			'desc' 		=> __( 'Some themes filter the menu item classes and strip out core WordPress functionality.  This will change the structure of ShiftNav and prevent styles from being applies.  This will prevent any actions on the <code>nav_menu_css_class</code> filter.', 'shiftnav' ),
			'type' 		=> 'checkbox',
			'default' 	=> 'off'
		),

		
		
		/*
		array(
			'name' => 'multicheck',
			'label' => __( 'Multile checkbox', 'shiftnav' ),
			'desc' => __( 'Multi checkbox description', 'shiftnav' ),
			'type' => 'multicheck',
			'options' => array(
				'one' => 'One',
				'two' => 'Two',
				'three' => 'Three',
				'four' => 'Four'
			)
		),
		array(
			'name' => 'selectbox',
			'label' => __( 'A Dropdown', 'shiftnav' ),
			'desc' => __( 'Dropdown description', 'shiftnav' ),
			'type' => 'select',
			'default' => 'no',
			'options' => array(
				'yes' => 'Yes',
				'no' => 'No'
			)
		)
		*/
		
	);


	return $fields;
}

function shiftnav_get_settings_sections(){

	$prefix = SHIFTNAV_PREFIX;

	$sections = array(
		/*array(
			'id' => $prefix.'basics',
			'title' => __( 'Basic Configuration', 'shiftnav' )
		),*/
		array(
			'id' => $prefix.'shiftnav-main',
			'title' => __( 'Main ShiftNav Settings', 'shiftnav' )
		),
		array(
			'id' => $prefix.'togglebar',
			'title' => __( 'Toggle Bar', 'shiftnav' )
		)
	);

	$sections = apply_filters( 'shiftnav_settings_panel_sections' , $sections );

	$sections[] = array(
		'id'	=> $prefix.'general',
		'title'	=> __( 'General Settings' , 'shiftnav' ),
	);

	return $sections;

}

/**
 * Registers settings section and fields
 */
function shiftnav_admin_init() {

	$prefix = SHIFTNAV_PREFIX;
 
 	$sections = shiftnav_get_settings_sections();
 	$fields = shiftnav_get_settings_fields();

 	//set up defaults so they are accessible
	_SHIFTNAV()->set_defaults( $fields );

	
	$settings_api = _SHIFTNAV()->settings_api();

	//set sections and fields
	$settings_api->set_sections( $sections );
	$settings_api->set_fields( $fields );

	//initialize them
	$settings_api->admin_init();

}
add_action( 'admin_init', 'shiftnav_admin_init' );

function shiftnav_init_frontend_defaults(){
	if( !is_admin() ){
		_SHIFTNAV()->set_defaults( shiftnav_get_settings_fields() );
	}
}
add_action( 'init', 'shiftnav_init_frontend_defaults' );

/**
 * Register the plugin page
 */
function shiftnav_admin_menu() {
	add_submenu_page(
		'themes.php',
		'ShiftNav Settings',
		'ShiftNav',
		'manage_options',
		'shiftnav-settings',
		'shiftnav_settings_panel'
	);
	//add_options_page( 'Settings API', 'Settings API', 'manage_options', 'settings_api_test', 'shiftnav_plugin_page' );
}
 
add_action( 'admin_menu', 'shiftnav_admin_menu' );


function shiftnav_get_nav_menu_ops(){
	$menus = wp_get_nav_menus( array('orderby' => 'name') );
	$m = array( '_none' => 'Choose Menu, or use Theme Location Setting' );
	foreach( $menus as $menu ){
		$m[$menu->slug] = $menu->name;
	}
	return $m;
}

function shiftnav_get_theme_location_ops(){
	$locs = get_registered_nav_menus();
	$default = array( '_none' => 'Select Theme Location or use Menu Setting' );
	//$locs = array_unshift( $default, $locs );
	$locs = $default + $locs;
	//shiftp( $locs );
	return $locs;
}


/**
 * Display the plugin settings options page
 */
function shiftnav_settings_panel() {
	
	$settings_api = _SHIFTNAV()->settings_api();
 
	?>

	<div class="wrap">
	
	<?php settings_errors(); ?>

	<div class="shiftnav-settings-links">
		<?php do_action( 'shiftnav_settings_before_title' ); ?>
	</div>

	<h2>ShiftNav <?php if( SHIFTNAV_PRO ) echo 'Pro <i class="fa fa-rocket"></i>'; ?></h2>

	<?php

	do_action( 'shiftnav_settings_before' );	
 
	$settings_api->show_navigation();
	$settings_api->show_forms();

	do_action( 'shiftnav_settings_after' );
 
	?>

	</div>

	<?php
}




/**
 * Get the value of a settings field
 *
 * @param string $option settings field name
 * @param string $section the section name this field belongs to
 * @param string $default default text if it's not found
 * @return mixed
 */
function shiftnav_op( $option, $section, $default = null ) {
 
	$options = get_option( SHIFTNAV_PREFIX.$section );

	if ( isset( $options[$option] ) ) {
		return $options[$option];
	}

	if( $default == null ){
		//$default = _SHIFTNAV()->settings_api()->get_default( $option, SHIFTNAV_PREFIX.$section );
		$default = _SHIFTNAV()->get_default( $option, SHIFTNAV_PREFIX.$section );
	}

	return $default;
}
function shiftnav_get_instance_options( $instance ){
	//echo SHIFTNAV_PREFIX.$instance;
	$defaults = _SHIFTNAV()->get_defaults( SHIFTNAV_PREFIX.$instance );
	$options = get_option( SHIFTNAV_PREFIX.$instance , $defaults );
	if( !is_array( $options ) || count( $options ) == 0 ) return $defaults;
	return $options;
}

function shiftnav_admin_panel_styles(){
	?>
<style>

</style>
	<?php
}
//add_action( 'admin_head-appearance_page_shiftnav-settings' , 'shiftnav_admin_panel_styles' );

function shiftnav_admin_panel_assets( $hook ){

	if( $hook == 'appearance_page_shiftnav-settings' ){
		wp_enqueue_script( 'shiftnav' , SHIFTNAV_URL . 'admin/assets/admin.settings.js' );
		wp_enqueue_style( 'shiftnav-settings-styles' , SHIFTNAV_URL.'admin/assets/admin.settings.css' );
		wp_enqueue_style( 'shiftnav-font-awesome' , SHIFTNAV_URL.'assets/css/fontawesome/css/font-awesome.min.css' );
	}
}
add_action( 'admin_enqueue_scripts' , 'shiftnav_admin_panel_assets' );



function shiftnav_check_menu_assignment(){
	$display = shiftnav_op(  'display_main' , 'shiftnav-main' );

	if( $display == 'on' ){
		if( !has_nav_menu( 'shiftnav' ) ){
			?>
			<div class="update-nag"><strong>Important!</strong> There is no menu assigned to the <strong>ShiftNav [Main]</strong> Menu Location.  <a href="<?php echo admin_url( 'nav-menus.php?action=locations' ); ?>">Assign a menu</a></div>
			<br/><br/>
			<?php
		}
	}
}
add_action( 'shiftnav_settings_before' , 'shiftnav_check_menu_assignment' );

function shiftnav_allow_html( $str ){
	return $str;
}
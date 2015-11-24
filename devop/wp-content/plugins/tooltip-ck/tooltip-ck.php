<?php
/**
 * Plugin Name: Tooltip CK
 * Plugin URI: http://www.wp-pluginsck.com/en/wordpress-plugins/tooltip-ck
 * Description: Tooltip CK allows you to put some nice tooltip effects into your content. Example : {tooltip}Text to hover{end-text}a friendly little boy{end-tooltip}
 * Version: 1.0.7
 * Author: Cédric KEIFLIN
 * Author URI: http://www.wp-pluginsck.com/
 * License: GPL2
 */

defined('ABSPATH') or die;

// Make sure we don't expose any info if called directly
if ( !function_exists( 'add_action' ) ) {
	header('Status: 403 Forbidden');
	header('HTTP/1.1 403 Forbidden');
	exit;
}

// check if the free version is already loaded
if (!class_exists("Tooltipck") || !file_exists(WP_PLUGIN_DIR . '/tooltip-ck-pro/tooltip-ck-pro.php')) { 
// load the plugin class
class Tooltipck {

	public $pluginname, $pluginurl, $plugindir, $options, $settings, $settings_field, $ispro, $prourl;

	public $default_settings = 
	array( 	
			'fxduration' => '300',
			'dureebulle' => '500',
			'fxtransition' => 'linear',
			'stylewidth' => '150',
			'padding' => '5',
			'tipoffsetx' => '0',
			'tipoffsety' => '0',
			'opacity' => '0.8',
			'bgcolor1' => '#f0f0f0',
			'bgcolor2' => '#e3e3e3',
			'textcolor' => '#444444',
			'roundedcornerstl' => '5',
			'roundedcornerstr' => '5',
			'roundedcornersbr' => '5',
			'roundedcornersbl' => '5',
			'shadowcolor' => '#444444',
			'shadowblur' => '3',
			'shadowspread' => '0',
			'shadowoffsetx' => '0',
			'shadowoffsety' => '0',
			'shadowinset' => '0',
			'bordercolor' => '#efefef',
			'borderwidth' => '1'
			);

	function __construct() {
		$this->pluginname = 'tooltip-ck';
		$this->settings_field = 'tooltipck_options';
		$this->options = get_option( $this->settings_field );
		$this->prourl = 'http://www.wp-pluginsck.com/en/wordpress-plugins/tooltip-ck';
		$this->plugindir = plugin_dir_path( __FILE__ );
		$this->pluginurl = plugins_url( '', __FILE__ );
		$this->ispro = file_exists($this->plugindir . '/includes/class-' . $this->pluginname . '-pro.php');
	}

	function init() {
		if (is_admin()) {
			// load the pro version
			if (file_exists($this->plugindir . '/includes/class-' . $this->pluginname . '-pro.php')) {
				$this->ispro = true;
				if (!class_exists('Tooltipck_Pro')) {
					require($this->plugindir . '/includes/class-' . $this->pluginname . '-pro.php');
					new Tooltipck_Pro();
				}
			}

			// load settings page
			if (!class_exists("Tooltipck_Settings")) {
				require($this->plugindir . '/includes/class-' . $this->pluginname . '-settings.php');
				$this->settings = new Tooltipck_Settings();
			}
		} else {
			// load frontend tooltip class
			if (!class_exists("Tooltipck_Front")) {
				require($this->plugindir . '/includes/class-' . $this->pluginname . '-front.php');
				$tooltipck = new Tooltipck_Front();
				// $tooltipck->init();
			}
		}

		// add the get pro link in the plugins list
		add_filter( 'plugin_action_links', array( $this, 'show_pro_message_action_links'), 10, 2 );
	}

	function show_pro_message_action_links($links, $file) {
		if ($file == plugin_basename(__FILE__)) {
			array_push($links, '<a href="options-general.php?page=' . $this->pluginname . '">'. __('Settings'). '</a>');
			if (!$this->ispro) {
				array_push($links, '<br /><img class="iconck" src="' .$this->pluginurl . '/images/star.png" /><a target="_blank" href="' . $this->prourl .'">' . __('Get the PRO Version') . '</a>');
			} else {
				array_push($links, '<br /><img class="iconck" src="' .$this->pluginurl . '/images/tick.png" /><span style="color: green;">' . __('You are using the PRO Version. Thank you !') . '</span>' );
			}
		}
		return $links;
	}
}

$tooltipckClass = new Tooltipck();
$tooltipckClass->init();
}


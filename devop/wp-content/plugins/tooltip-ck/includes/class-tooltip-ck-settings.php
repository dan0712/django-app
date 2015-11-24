<?php
defined('ABSPATH') or die;

// Make sure we don't expose any info if called directly
if (!function_exists('is_admin')) {
	header('Status: 403 Forbidden');
	header('HTTP/1.1 403 Forbidden');
	exit();
}

if (!class_exists("Tooltipck_Settings")) :
class Tooltipck_Settings extends Tooltipck {

	var $pagehook;

	function __construct() {
		parent::__construct();

		add_action( 'admin_init', array($this, 'admin_init'), 20 );
		add_action( 'admin_menu', array($this, 'admin_settings_menu'), 20 );
	}

	function admin_settings_menu() {
		if ( ! current_user_can('update_plugins') )
			return;

		// add a new submenu to the standard Settings panel
		$this->pagehook = $page =  add_options_page(
		__('Tooltip CK', 'tooltipck'), __('Tooltip CK', 'tooltipck'), 
		'administrator', $this->pluginname, array($this,'render_options') );

		// executed on-load. Add all metaboxes and create the row in the options table
		add_action( 'load-' . $page, array( $this, 'add_metaboxes' ) );
		// load the assets for the plugin page only
		add_action("admin_head-$page", array($this, 'load_assets') );
	}

	function load_assets() {
		wp_enqueue_style('wp-color-picker');
		wp_enqueue_script('postbox');
		wp_enqueue_script('tooltipck_adminscript', $this->pluginurl . '/assets/tooltipck_admin.js', array('jquery', 'jquery-ui-button', 'wp-color-picker'));
		?>
		<style type="text/css">
		#ckwrapper label { float: left; width: 180px; }
		#ckwrapper input { max-width: 100%; }
		#ckwrapper .ckheading { color: #2EA2CC; font-weight: bold; }
		#ckwrapper span { display: inline-block; }
		#ckwrapper .wp-color-result, #ckwrapper img, #ckwrapper fieldset { vertical-align: middle; }
		.settings-error { clear: both; }
		</style>
	<?php }

	function admin_init() {
		register_setting( $this->settings_field, $this->settings_field);
	}

	function get_field($type, $name, $value, $classname = '', $optionsgroup = '') {
		if (!class_exists('Tooltipck_CKfields'))
			require($this->plugindir . '/cklibrary/class-ckfields.php');
		$ckfields = new Tooltipck_CKfields();
		$ckfields->pluginurl = $this->pluginurl;
		return $ckfields->get($type, $name, $value, $classname, $optionsgroup);
	}

	function get_field_name( $name ) {
		return sprintf( '%s[%s]', $this->settings_field, $name );
	}

	function get_field_value( $key, $default = null ) {
		if (isset($this->options[$key])) {
			return $this->options[$key];
		} else {
			if ($default == null && isset($this->default_settings[$key])) 
				return $this->default_settings[$key];
		}
		return $default;
	}

	function add_metaboxes() {
		// set the entry in the database options table if not exists
		add_option( $this->settings_field, $this->default_settings );
		// add the metaboxes
		add_meta_box( 'tooltipck-styles', __('Tooltip CK Styles'), array( $this, 'create_metabox_styles' ), $this->pagehook, 'main' );
		add_meta_box( 'tooltipck-effects', __('Tooltip CK Effects'), array( $this, 'create_metabox_effects' ), $this->pagehook, 'main' );
	}

	function create_metabox_styles() {
		?>
		<div class="ckheading"><?php _e('Colors ans Styles') ?></div>
		<div>
			<label for="<?php echo $this->get_field_name( 'bgcolor1' ); ?>"><?php _e( 'Background Color'); ?></label>
			<img class="iconck" src="<?php echo $this->pluginurl ?>/images/color.png" />
			<?php echo $this->get_field('color', $this->get_field_name( 'bgcolor1' ), $this->get_field_value( 'bgcolor1')) ?>
			<?php echo $this->get_field('color', $this->get_field_name( 'bgcolor2' ), $this->get_field_value( 'bgcolor2')) ?>
		</div>
		<div>
			<label for="<?php echo $this->get_field_name( 'bgimage' ); ?>"><?php _e( 'Background Image'); ?></label>
			<img class="iconck" src="<?php echo $this->pluginurl ?>/images/image.png" />
			<?php echo $this->get_field('media', $this->get_field_name( 'bgimage' ), $this->get_field_value( 'bgimage')) ?>
			<span><img class="iconck" src="<?php echo $this->pluginurl ?>/images/offsetx.png" /></span><span style="width:30px;"><?php echo $this->get_field('text', $this->get_field_name( 'bgpositionx' ), $this->get_field_value( 'bgpositionx')) ?></span>
			<span><img class="iconck" src="<?php echo $this->pluginurl ?>/images/offsety.png" /></span><span style="width:30px;"><?php echo $this->get_field('text', $this->get_field_name( 'bgpositiony' ), $this->get_field_value( 'bgpositiony')) ?></span>
			<?php $options_bgrepeat = array(
				'repeat' =>'img:'.$this->pluginurl.'/images/bg_repeat.png'
				, 'repeat-x'=>'img:'.$this->pluginurl.'/images/bg_repeat-x.png'
				, 'repeat-y'=>'img:'.$this->pluginurl.'/images/bg_repeat-y.png'
				, 'no-repeat'=>'img:'.$this->pluginurl.'/images/bg_no-repeat.png'
				);
			?>
				<span><?php echo $this->get_field('radio', $this->get_field_name( 'bgimagerepeat' ), $this->get_field_value( 'bgimagerepeat'), '', $options_bgrepeat) ?></span>
		</div>
		<div>
			<label for="<?php echo $this->get_field_name( 'opacity' ); ?>"><?php _e( 'Opacity'); ?></label>
			<img class="iconck" src="<?php echo $this->pluginurl ?>/images/layers.png" />
			<?php echo $this->get_field('text', $this->get_field_name( 'opacity' ), $this->get_field_value( 'opacity')) ?>
		</div>
		<div>
			<label for="<?php echo $this->get_field_name( 'textcolor' ); ?>"><?php _e( 'Text Color'); ?></label>
			<img class="iconck" src="<?php echo $this->pluginurl ?>/images/color.png" />
			<?php echo $this->get_field('color', $this->get_field_name( 'textcolor' ), $this->get_field_value( 'textcolor')) ?>
		</div>
		<div>
			<label for="<?php echo $this->get_field_name( 'roundedcorners' ); ?>"><?php _e( 'Border radius'); ?></label>
			<img class="iconck" src="<?php echo $this->pluginurl ?>/images/border_radius_tl.png" />
			<span><?php _e( 'Top left'); ?></span><span style="width:30px;"><?php echo $this->get_field('text', $this->get_field_name( 'roundedcornerstl' ), $this->get_field_value( 'roundedcornerstl')) ?></span>
			<span><?php _e( 'Top right'); ?></span><span style="width:30px;"><?php echo $this->get_field('text', $this->get_field_name( 'roundedcornerstr' ), $this->get_field_value( 'roundedcornerstr')) ?></span>
			<span><?php _e( 'Bottom right'); ?></span><span style="width:30px;"><?php echo $this->get_field('text', $this->get_field_name( 'roundedcornersbr' ), $this->get_field_value( 'roundedcornersbr')) ?></span>
			<span><?php _e( 'Bottom left'); ?></span><span style="width:30px;"><?php echo $this->get_field('text', $this->get_field_name( 'roundedcornersbl' ), $this->get_field_value( 'roundedcornersbl')) ?></span>
		</div>
		<div>
			<label for="<?php echo $this->get_field_name( 'shadowcolor' ); ?>"><?php _e( 'Shadow'); ?></label>
			<img class="iconck" src="<?php echo $this->pluginurl ?>/images/shadow_blur.png" />
			<span><?php echo $this->get_field('color', $this->get_field_name( 'shadowcolor' ), $this->get_field_value( 'shadowcolor')) ?></span>
			<span><?php _e( 'Blur'); ?></span><span style="width:30px;"><?php echo $this->get_field('text', $this->get_field_name( 'shadowblur' ), $this->get_field_value( 'shadowblur')) ?></span>
			<span><?php _e( 'Spread'); ?></span><span style="width:30px;"><?php echo $this->get_field('text', $this->get_field_name( 'shadowspread' ), $this->get_field_value( 'shadowspread')) ?></span>
			<span><?php _e( 'Offset X'); ?></span><span style="width:30px;"><?php echo $this->get_field('text', $this->get_field_name( 'shadowoffsetx' ), $this->get_field_value( 'shadowoffsetx')) ?></span>
			<span><?php _e( 'Offset Y'); ?></span><span style="width:30px;"><?php echo $this->get_field('text', $this->get_field_name( 'shadowoffsety' ), $this->get_field_value( 'shadowoffsety')) ?></span>
		</div>
		<div>
			<label for="<?php echo $this->get_field_name( 'bordercolor' ); ?>"><?php _e( 'Border'); ?></label>
			<img class="iconck" src="<?php echo $this->pluginurl ?>/images/shape_square.png" />
			<span><?php echo $this->get_field('color', $this->get_field_name( 'bordercolor' ), $this->get_field_value( 'bordercolor')) ?></span>
			<span style="width:30px;"><?php echo $this->get_field('text', $this->get_field_name( 'borderwidth' ), $this->get_field_value( 'borderwidth')) ?></span> px
		</div>
		<div class="ckheading"><?php _e('Dimensions and Position') ?></div>
		<div>
			<label for="<?php echo $this->get_field_name( 'stylewidth' ); ?>"><?php _e( 'Tooltip width'); ?></label>
			<img class="iconck" src="<?php echo $this->pluginurl ?>/images/width.png" />
			<?php echo $this->get_field('text', $this->get_field_name( 'stylewidth' ), $this->get_field_value( 'stylewidth')) ?>px
		</div>
		<div>
			<label for="<?php echo $this->get_field_name( 'tipoffsetx' ); ?>"><?php _e( 'Tooltip Offset X'); ?></label>
			<img class="iconck" src="<?php echo $this->pluginurl ?>/images/offsetx.png" />
			<?php echo $this->get_field('text', $this->get_field_name( 'tipoffsetx' ), $this->get_field_value( 'tipoffsetx')) ?>px
		</div>
		<div>
			<label for="<?php echo $this->get_field_name( 'tipoffsety' ); ?>"><?php _e( 'Tooltip Offset Y'); ?></label>
			<img class="iconck" src="<?php echo $this->pluginurl ?>/images/offsety.png" />
			<?php echo $this->get_field('text', $this->get_field_name( 'tipoffsety' ), $this->get_field_value( 'tipoffsety')) ?>px
		</div>
	<?php }

	function create_metabox_effects() {
		?>
		<div>
			<label for="<?php echo $this->get_field_name( 'fxduration' ); ?>"><?php _e( 'Tooltip opening duration'); ?></label>
			<img class="iconck" src="<?php echo $this->pluginurl ?>/images/hourglass.png" />
			<?php echo $this->get_field('text', $this->get_field_name( 'fxduration' ), $this->get_field_value( 'fxduration')) ?>ms
		</div>
		<div>
			<label for="<?php echo $this->get_field_name( 'dureebulle' ); ?>"><?php _e( 'Tooltip before close time'); ?></label>
			<img class="iconck" src="<?php echo $this->pluginurl ?>/images/hourglass.png" />
			<?php echo $this->get_field('text', $this->get_field_name( 'dureebulle' ), $this->get_field_value( 'dureebulle')) ?>ms
		</div>
	<?php }

	function render_options() {
	?>
	<div id="ckwrapper" class="wrap">
		<img src="<?php echo $this->pluginurl ?>/images/logo_tooltipck_64.png" style="float:left; margin: 0px 5px 5px 0;" />
		<h2><?php esc_attr_e('Tooltip CK Settings');?></h2>
		<?php $this->show_pro_message_settings_page(); ?>
		<form method="post" action="options.php">
			<div style="clear:both;">
				<input type="submit" class="button button-primary" name="save_options" value="<?php esc_attr_e('Save Settings'); ?>" />
			</div>
			<div class="metabox-holder">
				<div class="postbox-container" style="width: 99%;">
				<?php 
					settings_fields($this->settings_field); 
					do_meta_boxes( $this->pagehook, 'main', null );
				?>
				</div>
			</div>
			<div>
				<input type="submit" class="button button-primary" name="save_options" value="<?php esc_attr_e('Save Settings'); ?>" />
			</div>
		</form>
		<?php $this->show_pro_message_settings_page(); ?>
	</div>
	<!-- Needed to allow metabox layout and close functionality. -->
	<script type="text/javascript">
		//<![CDATA[
		jQuery(document).ready( function ($) {
			postboxes.add_postbox_toggles('<?php echo $this->pagehook; ?>');
		});
		//]]>
	</script>
	<?php }

	function show_pro_message_settings_page() { ?>
		<div class="ckcheckproversion">
			<?php if (! $this->ispro ) : ?>
				<img class="iconck" src="<?php echo $this->pluginurl ?>/images/star.png" />
				<a target="_blank" href="<?php echo $this->prourl ?>"><?php _e('Get the PRO Version'); ?></a>
			<?php endif; ?>
		</div>
	<?php }
}
endif;
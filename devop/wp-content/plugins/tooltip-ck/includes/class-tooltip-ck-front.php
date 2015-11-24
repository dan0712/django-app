<?php
defined('ABSPATH') or die;

// Make sure we don't expose any info if called directly
if ( !function_exists( 'add_action' ) ) {
	header('Status: 403 Forbidden');
	header('HTTP/1.1 403 Forbidden');
	exit;
}

if (!class_exists("Tooltipck_Front")) :
class Tooltipck_Front extends Tooltipck {

	function __construct() {
		parent::__construct();

		add_action('wp_head', array( $this, 'load_assets'));
		add_action('init', array( $this, 'load_assets_files'));
		add_action('template_redirect',array( $this, 'do_my_ob_start') );
	}

	function do_my_ob_start() {
		ob_start(array($this, 'search_key') );
	}

	function load_assets_files() {
		wp_enqueue_script('jquery');
		wp_enqueue_script('jquery-ui-core ');
		wp_enqueue_style('tooltipck', $this->pluginurl . '/assets/tooltipck.css');
		wp_enqueue_script('tooltipck', $this->pluginurl . '/assets/tooltipck.js');
	}

	function load_assets() {
		// mobile detection
		if (!class_exists('Mobile_Detect')) {
			require_once dirname(__FILE__) . '/Mobile_Detect.php';
		}
		$detect = new Mobile_Detect;
		// $this->load_assets_files();
		
		$fxduration = $this->get_option('fxduration');
		$dureebulle = $this->get_option('dureebulle');
		$opacity = $this->get_option('opacity');
		$fxtransition = 'linear';
		?>
		<script type="text/javascript">
		jQuery(document).ready(function(){
			jQuery(this).Tooltipck({ 
				fxtransition: '<?php echo $fxtransition?>', 
				fxduration: <?php echo $fxduration ?>, 
				dureebulle: <?php echo $dureebulle ?>, 
				opacite: <?php echo $opacity ?>,
				ismobile: <?php echo ($detect->isMobile() ? '1' : '0') ?>
			});
		});
		</script>
		<style type="text/css">
		<?php echo $this->create_tooltip_css(); ?>
		</style>
	<?php }

	function get_option($name) {
		if (isset($this->options[$name])) {
			return $this->options[$name];
		} else if (isset($this->default_settings[$name])) {
			return $this->default_settings[$name];
		}
		return null;
	}

	function search_key($content){
		// test if the plugin is needed
		if (!stristr($content, "{tooltip}"))
			return $content;
		
		$regex = "#{tooltip}(.*?){end-tooltip}#s"; // search mask
		$content = preg_replace_callback($regex, array('Tooltipck_Front', 'create_tooltip'), $content);

		return $content;
	}

	function create_tooltip(&$matches) {
		$ID = (int) (microtime() * 100000); // unique ID
		$stylewidth = $this->get_option('stylewidth');
		$fxduration = $this->get_option('fxduration');
		$dureebulle = $this->get_option('dureebulle');
		$tipoffsetx = $this->get_option('tipoffsetx');
		$tipoffsety = $this->get_option('tipoffsety');

		// get the text
		$patterns = "#{tooltip}(.*){(.*)}(.*){end-tooltip}#Uis";
		$result = preg_match($patterns, $matches[0], $results);

		// check if there is some custom params
		$relparams = Array();
		$params = explode('|', $results[2]);
		$parmsnumb = count($params);
		for ($i = 1; $i < $parmsnumb; $i++) {
			$fxduration = stristr($params[$i], "mood=") ? str_replace('mood=', '', $params[$i]) : $fxduration;
			$dureebulle = stristr($params[$i], "tipd=") ? str_replace('tipd=', '', $params[$i]) : $dureebulle;
			$tipoffsetx = stristr($params[$i], "offsetx=") ? str_replace('offsetx=', '', $params[$i]) : $tipoffsetx;
			$tipoffsety = stristr($params[$i], "offsety=") ? str_replace('offsety=', '', $params[$i]) : $tipoffsety;
			$stylewidth = stristr($params[$i], "w=") ? str_replace('px', '', str_replace('w=', '', $params[$i])) : $stylewidth;
		}

		// compile the rel attribute to inject the specific params
		$relparams['mood'] = 'mood=' . $fxduration;
		$relparams['tipd'] = 'tipd=' . $dureebulle;
		$relparams['offsetx'] = 'offsetx=' . $tipoffsetx;
		$relparams['offsety'] = 'offsety=' . $tipoffsety;

		$tooltiprel = '';
		if (count($relparams)) {
			$tooltiprel = ' rel="' . implode("|", $relparams) . '"';
		}

		// output the code
		$result = '<span class="infotip" id="tooltipck' . $ID . '"' . $tooltiprel . '>'
					. $results[1]
					. '<span class="tooltipck_tooltip" style="width:' . $stylewidth . 'px;">'
						. '<span class="tooltipck_inner">'
						. $results[3]
						. '</span>'
					. '</span>'
				. '</span>';

		return $result;
	}

	function create_tooltip_css() {
		$padding = $this->get_option('padding') . 'px';
		$tipoffsetx = $this->get_option('tipoffsetx') . 'px';
		$tipoffsety = $this->get_option('tipoffsety') . 'px';
		$bgcolor1 = $this->get_option('bgcolor1');
		$bgcolor2 = $this->get_option('bgcolor2');
		$textcolor = $this->get_option('textcolor');
		$roundedcornerstl = $this->get_option('roundedcornerstl') . 'px';
		$roundedcornerstr = $this->get_option('roundedcornerstr') . 'px';
		$roundedcornersbr = $this->get_option('roundedcornersbr') . 'px';
		$roundedcornersbl = $this->get_option('roundedcornersbl') . 'px';
		$shadowcolor = $this->get_option('shadowcolor');
		$shadowblur = $this->get_option('shadowblur') . 'px';
		$shadowspread = $this->get_option('shadowspread') . 'px';
		$shadowoffsetx = $this->get_option('shadowoffsetx') . 'px';
		$shadowoffsety = $this->get_option('shadowoffsety') . 'px';
		$bordercolor = $this->get_option('bordercolor');
		$borderwidth = $this->get_option('borderwidth') . 'px';
		$shadowinset = $this->get_option('shadowinset');
		$shadowinset = $shadowinset ? 'inset ' : '';

		$background = ( $this->get_option('bgimage') ) ? 'background-image: url("' . get_site_url() . '/' . $this->get_option('bgimage') . '")' . ';' : '';
		$background .= ( $this->get_option('bgimage') AND $this->get_option('bgimagerepeat') ) ? 'background-repeat: ' . $this->get_option('bgimagerepeat') . ';' : '';
		$background .= ( $this->get_option('bgimage') AND ($this->get_option('bgpositionx') || $this->get_option('bgpositiony')) ) ? 'background-position: ' . $this->get_option('bgpositionx') . ' ' . $this->get_option('bgpositiony') . ';' : '';

		$css = '.tooltipck_tooltip {'
				. 'padding: ' . $padding . ';'
				. 'border: ' . $bordercolor . ' ' . $borderwidth . ' solid;'
				. '-moz-border-radius: ' . $roundedcornerstl . ' ' . $roundedcornerstr . ' ' . $roundedcornersbr . ' ' . $roundedcornersbl . ';'
				. '-webkit-border-radius: ' . $roundedcornerstl . ' ' . $roundedcornerstr . ' ' . $roundedcornersbr . ' ' . $roundedcornersbl . ';'
				. 'border-radius: ' . $roundedcornerstl . ' ' . $roundedcornerstr . ' ' . $roundedcornersbr . ' ' . $roundedcornersbl . ';'
				. 'background-color: ' . $bgcolor1 . ';'
				. 'background-image: -moz-linear-gradient(top, ' . $bgcolor1 . ', ' . $bgcolor2 . ');'
				. 'background-image: -webkit-gradient(linear, 0% 0%, 0% 100%, from(' . $bgcolor1 . '), to(' . $bgcolor2 . '));'
				. $background
				. 'color: ' . $textcolor . ';'
				. 'margin: ' . $tipoffsety . ' 0 0 ' . $tipoffsetx . ';'
				. '-moz-box-shadow: ' . $shadowinset . $shadowoffsetx . ' ' . $shadowoffsety . ' ' . $shadowblur . ' ' . $shadowspread . ' ' . $shadowcolor . ';'
				. '-webkit-box-shadow: ' . $shadowinset . $shadowoffsetx . ' ' . $shadowoffsety . ' ' . $shadowblur . ' ' . $shadowspread . ' ' . $shadowcolor . ';'
				. 'box-shadow: ' . $shadowinset . $shadowoffsetx . ' ' . $shadowoffsety . ' ' . $shadowblur . ' ' . $shadowspread . ' ' . $shadowcolor . ';'
				. '}';

		return $css;
	}
}
endif;

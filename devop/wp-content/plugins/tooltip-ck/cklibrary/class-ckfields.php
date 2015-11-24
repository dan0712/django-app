<?php
defined('ABSPATH') or die;

if (!class_exists("Tooltipck_CKfields")) :
class Tooltipck_CKfields {

	private $name, $id, $value, $classname, $optionsgroup, $isfiles, $attribs;
	
	public $pluginurl;

	function __construct() {
	}

	public function get($type, $name, $value, $classname = '', $optionsgroup = '', $isfiles = false, $attribs = '') {
		$this->name = $name;
		$this->id = trim(preg_replace('#\W#', '_', $name), '_');
		$this->value = $value;
		$this->optionsgroup = $optionsgroup;
		$this->classname = $classname;
		$this->isfiles = $isfiles;
		$this->attribs = $attribs;
		$function = 'get'.ucfirst($type);
		return $this->$function();
	}

	private function getColor() {
		wp_enqueue_script( 'ckcolor', $this->pluginurl . '/cklibrary/ckfields/ckcolor/ckcolor.js', array('jquery', 'jquery-ui-button', 'wp-color-picker') );
		$class = $this->classname ? ' class="ck-color-field '.$this->classname.'"' : ' class="ck-color-field"';
		$html = '<input type="text" id="'.$this->id.'" name="'.$this->name.'" value="'.$this->value.'"'.$class.' data-default-color="'.$this->value.'" />';
		return $html;
	}

	private function getText() {
		$class = $this->classname ? ' class="'.$this->classname.'"' : '';
		$html = '<input type="text" id="'.$this->id.'" name="'.$this->name.'" value="'.$this->value.'"'.$class.' />';
		return $html;
	}

	private function getSelect() {
		$class = $this->classname ? ' class="'.$this->classname.'"' : '';
		$html = '<select id="'.$this->id.'" name="'.$this->name.'" value="'.$this->value.'"'.$class.' '.$this->attribs.' >';
		$html .= $this->getOptions();
		$html .= '</select>';
		return $html;
	}

	private function getOptions() {
		if (!is_array($this->optionsgroup)) {
			$this->getArrayFromOptions();
		}
		$optionshtml = array();
		foreach ($this->optionsgroup as $val => $name) {
			if ( $this->isfiles == true ) {
				$val = $name;
			}
			if ($val == $this->value) {
				$optionshtml[] = '<option value="'.$val.'" selected="selected">'.$name.'</option>';
			} else {
				$optionshtml[] = '<option value="'.$val.'">'.$name.'</option>';
			}
		}
		return implode('', $optionshtml);
	}
	
	private function getArrayFromOptions() {
		$this->optionsgroup = rtrim($this->optionsgroup, '</option>');
		$this->optionsgroup = explode('</option>', $this->optionsgroup);
		$optionsgroup = array();
		foreach ($this->optionsgroup as $option) {
			$option = explode('">', $option);
			$optionsgroup[str_replace( '<option value="', '', trim($option[0]))] = $option[1];
		}
		$this->optionsgroup = $optionsgroup;
	}
	
	private function getRadio() {
		wp_enqueue_style( 'ckradio2', $this->pluginurl . '/cklibrary/ckfields/ckradio2/ckradio2.css' );
		wp_enqueue_script( 'ckradio2', $this->pluginurl . '/cklibrary/ckfields/ckradio2/ckradio2.js', array('jquery') );
		if (!is_array($this->optionsgroup)) {
			$this->getArrayFromOptions();
		}
		$class = $this->classname ? ' class="'.$this->classname.'"' : '';
		$html = array();

		// Start the radio field output.
		$html[] = '<fieldset id="' . $this->id . '-fieldset" style="padding-left:0px;" class="ckradio2" >';
		$html[] = '<input type="hidden" isradio="1" id="' . $this->id . '" name="' . $this->name . '"' . $class . ' value="'.$this->value.'" />';

		// Get the field options.
		$options = $this->optionsgroup;

		// Build the radio field output.
		foreach ($options as $value => $name) {
		// var_dump($i);var_dump($option);
			if (stristr($name,"img:")) $name = '<img src="' . str_replace("img:","",$name) . '" style="margin:0; float:none;" />';
			// Initialize some option attributes.
			$checked = ((string) $value == (string) $this->value) ? ' checked="checked"' : '';
			$checkedclass = ((string) $value == (string) $this->value) ? ' coche' : '';
			// $class = !empty($option->class) ? ' class="radio radioClass ' . $option->class . '"' : ' class="radio radioClass"';
			$class = ' class="radio radioClass"';
			// $labelclass = !empty($option->class) ? ' class="' . $option->class . '"' : '';
			// $disabled = !empty($option->disable) ? ' disabled="disabled"' : '';

			// Initialize some JavaScript option attributes.
			// $onclick = !empty($option->onclick) ? ' onclick="' . $option->onclick . '"' : '';
			//$onclick2 = ' onclick="$(\''.$this->id.'\').setProperty(\'value\',this.value);"' ;

			$html[] = '<span class="boutonRadio' . $checkedclass . '" style="" identifier="'.$this->id.'"><input type="radio" id="' . $this->id . $value . '" name="' . $this->name . '"' .
					' value="' . htmlspecialchars($value, ENT_COMPAT, 'UTF-8') . '"'
					. $checked . $class . ' style="margin-left:5px;" />';
			// $html[] = $optionicon ? '<img src="' . $this->getPathToElements() . '/images/' . $optionicon . '" style="float:none;" />' : '';
			$html[] = '<span>' . __($name) . '</span>';
			$html[] = '</span>';
		}

		// End the radio field output.
		$html[] = '</fieldset>';

		return implode($html);
	}
	
	private function getMedia() {
		wp_enqueue_media();
		wp_enqueue_script( 'ckmedia', $this->pluginurl . '/cklibrary/ckfields/ckmedia/ckmedia.js', array('jquery') );
		$class = $this->classname ? ' class="'.$this->classname.'"' : '';
		$html = '<input type="text" id="'.$this->id.'" name="'.$this->name.'" value="'.$this->value.'"'.$class.' />';
		$html .= '<a class="button button-secondary" onclick="open_media_managerck(this, \'' . get_site_url() . '/\');">'. __('Select') .'</a>';
		
		return $html;
	}
}
endif;
/*
*  ShiftNav.js
*  
*  http://shiftnav.io
*
*  Copyright Chris Mavricos, SevenSpark http://sevenspark.com
*/

;(function ( $, window, document, undefined ) {

	var pluginName = "shiftnav",
		defaults = {
			mouseEvents: true,
			retractors: true,
			touchOffClose: true,
			clicktest: false,
			windowstest: false,
			debug: false,
			swipe_tolerance_x: 150,			//min distance to swipe
			swipe_tolerance_y: 30,			//max vertical displacement
			swipe_edge_proximity: 70,		//maximum distance from edge
			open_current: false,
			collapse_accordions: false
		};

	function Plugin ( element, options ) {

		this.element = element;

		this.$shiftnav = $( this.element );
		this.$menu = this.$shiftnav.find( 'ul.shiftnav-menu' );

		this.settings = $.extend( {}, defaults, options );
		this._defaults = defaults;
		this._name = pluginName;

		this.touchenabled = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0) || (navigator.msMaxTouchPoints > 0);
		
		if( window.navigator.pointerEnabled ){
			this.touchStart = 'pointerdown';
			this.touchEnd	= 'pointerup';
			this.touchMove	= 'pointermove';
		}
		else if( window.navigator.msPointerEnabled ){
			this.touchStart = 'MSPointerDown';
			this.touchEnd	= 'MSPointerUp';
			this.touchMove	= 'MSPointerMove';
		}
		else{
			this.touchStart = 'touchstart';
			this.touchEnd	= 'touchend';
			this.touchMove	= 'touchmove';
		}

		this.toggleevent = this.touchEnd == 'touchend' ? this.touchEnd + ' click' : this.touchEnd;	//add click except for IE		
		this.transitionend = 'transitionend.shiftnav webkitTransitionEnd.shiftnav msTransitionEnd.shiftnav oTransitionEnd.shiftnav';

		//TESTING
		if( this.settings.clicktest ) this.touchEnd = 'click';

		this.init();
		
	}

	Plugin.prototype = {

		init: function () {


			this.$shiftnav.removeClass( 'shiftnav-nojs' );		//We're off and running

			//this.$toggles = $( '.shiftnav-toggle[data-shiftnav-target="'+this.$shiftnav.attr('id')+'"]' );
			this.$toggles = $( '.shiftnav-toggle[data-shiftnav-target="'+this.$shiftnav.data('shiftnav-id')+'"]' );

			//Initialize user interaction events

			this.initializeShiftNav();

			this.initializeTargets();
			this.initializeSubmenuToggleMouseEvents();
			this.initializeRetractors();
			this.initializeResponsiveToggle();
			this.initializeSwipeHandler();

			//this.initializeTouchoffClose();  //attached on open instead

		},



		/* Initalizers */

		initializeShiftNav: function(){
		
			var $body = $('body'),
				plugin = this;

			//Only enable the site once
			if( !$body.hasClass( 'shiftnav-enabled' ) ){
	
				$body.addClass( 'shiftnav-enabled' );
				if( shiftnav_data.lock_body == 'on' ) $body.addClass( 'shiftnav-lock' );
				if( shiftnav_data.lock_body_x == 'on' ) $body.addClass( 'shiftnav-lock-x' );
				
				if( shiftnav_data.shift_body != 'off' ) $body.wrapInner( '<div class="shiftnav-wrap"></div>' );	//unique
				else $body.addClass( 'shiftnav-disable-shift-body' );

				//Move elements outside of shifter
				$( '#shiftnav-toggle-main, #wpadminbar' ).appendTo( 'body' );

				var $wrap = $( '.shiftnav-wrap' );

				//Pad top
				var toggleHeight = $( '#shiftnav-toggle-main' ).outerHeight();
				$wrap.css( 'padding-top' , toggleHeight );
				if( shiftnav_data.shift_body == 'off' ) $body.css( 'padding-top' , toggleHeight );

				//Setup non-transform
				//Some browsers provide false positives for feature detection, so we have to do browser detection as well, sadly
				var fpos = false;	//falsePositive
				var ua = navigator.userAgent.toLowerCase();

				if( /android/.test( ua ) ){
					//always ignore old androids
					if( /android [1-3]/.test( ua ) ) fpos = true;
					//always allow Chrome
					else if( /chrome/.test( ua ) ) fpos = false;
					//Android 4.4+ is okay
					else if( /android 4.[4-9]/.test( ua ) ) fpos = false;
					else fpos = true;
				}

				if( !shift_supports( 'transform' ) || fpos ){
					$body.addClass( 'shiftnav-no-transforms' );
				}


				//Setup swipe open on MAIN SHIFTNAV only
				if( shiftnav_data.swipe_open == 'on' ){
					var wrap_start_y = 0,
						wrap_start_x = 0,
						wrap_cur_y = 0,
						wrap_cur_x = 0,
						viewport_width = $( window ).width();


					if( shiftnav_data.shift_body == 'off' ) $wrap = $( 'body' );

					$wrap.on( 'touchstart' , function( e ){
						wrap_start_y = e.originalEvent.changedTouches[0].pageY;
						wrap_start_x = e.originalEvent.changedTouches[0].pageX;
						//console.log( "START: " + wrap_start_x );
					});

					//Left edge activate on swipe from left
					if( $( '#shiftnav-main' ).hasClass( 'shiftnav-left-edge' ) ){
						$wrap.on( 'touchmove' , function( e ){
							wrap_cur_x = e.originalEvent.changedTouches[0].pageX;
							//console.log( wrap_cur_x );

							//if close to left edge 
							if( wrap_start_x < plugin.settings.swipe_edge_proximity ){
								e.preventDefault();

								//if swipe more than 150
								if( wrap_cur_x - wrap_start_x > plugin.settings.swipe_tolerance_x ){
									wrap_cur_y = e.originalEvent.changedTouches[0].pageY;
									if( Math.abs( wrap_cur_y - wrap_start_y ) < plugin.settings.swipe_tolerance_y ){
										plugin.openShiftNav();
										e.stopPropagation();
									}
								}
							}
						});
					}
					//Right edge activate on swipe from right
					else{
						$wrap.on( 'touchmove' , function( e ){
							wrap_cur_x = e.originalEvent.changedTouches[0].pageX;

							//if we start from the edge, tell android we've got this covered
							if( wrap_start_x > ( viewport_width - plugin.settings.swipe_edge_proximity ) ){
								e.preventDefault();

								//if swipe more than 150, open panel
								if( ( wrap_start_x - wrap_cur_x > plugin.settings.swipe_tolerance_x ) ){
									wrap_cur_y = e.originalEvent.changedTouches[0].pageY;
									if( Math.abs( wrap_cur_y - wrap_start_y ) < plugin.settings.swipe_tolerance_y ){
										plugin.openShiftNav();
										e.stopPropagation();
									}
								}
							}
							
							
						});
					}
				}

				//Handle searchbar toggle
				$( '.shiftnav-searchbar-toggle' ).on( this.toggleevent , function( e ){
					e.stopPropagation();
					e.preventDefault();

					var $drop = $( this ).next( '.shiftnav-searchbar-drop' );

					//Close
					if( $drop.hasClass( 'shiftnav-searchbar-drop-open' ) ){
						$drop.removeClass( 'shiftnav-searchbar-drop-open' );
						$( 'body' ).off( 'click.shiftnav-searchbar-drop' );
					}
					//Open
					else{
						$drop.addClass( 'shiftnav-searchbar-drop-open' );
						$drop.find( '.shiftnav-search-input' ).focus();

						//Close on click-off - can't do this immediately because IE is so damn dumb
						setTimeout( function(){
							$( 'body' ).on( 'click.shiftnav-searchbar-drop' , function( e ){
								$( '.shiftnav-searchbar-drop' ).removeClass( 'shiftnav-searchbar-drop-open' );
								$( 'body' ).off( 'click.shiftnav-searchbar-drop' );
							});
						}, 100);
					}
				});
				$( '.shiftnav-searchbar-drop' ).on( this.toggleevent , function( e ){
					e.stopPropagation();
				});
				$( '.shiftnav-searchbar-drop .shiftnav-search-input').on( 'blur' , function( e ){
					if( $( this ).val() == '' && !toggle_clicked ){
						$( this ).parents( '.shiftnav-searchbar-drop' ).removeClass( 'shiftnav-searchbar-drop-open' );
					}
				});
				var toggle_clicked;
				$( '.shiftnav-searchbar-toggle' ).on( 'mousedown' , function( e ){
					toggle_clicked = true;
				});
				$( '.shiftnav-searchbar-toggle' ).on( 'mouseup' , function( e ){
					toggle_clicked = false;
				});
				
				
			}

			this.$shiftnav.appendTo( 'body' );

			if( this.$shiftnav.hasClass( 'shiftnav-right-edge' ) ){
				this.edge = 'right';
			}
			else this.edge = 'left';

			this.openclass = 'shiftnav-open shiftnav-open-' + this.edge;

			//Set retractor heights
			this.$shiftnav.find( '.shiftnav-submenu-activation' ).each( function(){
				var length = $( this ).outerHeight();
				$( this ).css( { 'height' : length , 'width' : length } );

				//$( this ).css( 'height' , $( this ).parent( '.menu-item' ).height() );
			});



			//Current open
			if( plugin.settings.open_current ){
				$( '.shiftnav .shiftnav-sub-accordion.current-menu-item, .shiftnav .shiftnav-sub-accordion.current-menu-item-ancestor' ).addClass( 'shiftnav-active' );
			}
			
		},
	
		initializeTargets: function(){

			var plugin = this;

			this.$shiftnav.on( 'click' , '.shiftnav-target' , function( e ){
				var scrolltarget = $(this).data( 'shiftnav-scrolltarget' );
				if( scrolltarget ){
					var $target = $( scrolltarget ).first();
					if( $target.size() > 0 ){
						$( 'html,body' ).animate({
							scrollTop: $target.offset().top
						}, 1000 , 'swing' ,
						function(){
							plugin.closeShiftNav();	//close the menu after a successful scroll
						});
						return false; //don't follow any links if this scroll target is present
					}
					//if target isn't present here, redirect with hash
					else{
						var href = $(this).attr( 'href' );
						if( href && href.indexOf( '#' ) == -1 ){				//check that hash does not already exist
							if( scrolltarget.indexOf( '#' ) == -1 ){	//if this is a class, add a hash tag
								scrolltarget = '#'+scrolltarget;
							}
							window.location = href + scrolltarget;		//append hash/scroll target to URL and redirect
							e.preventDefault();
						}
						//No href, no worries
					}
				}
				else if( $( this ).is( 'span' ) ){
					var $li = $( this ).parent( '.menu-item' );
					if( $li.hasClass( 'shiftnav-active' ) ){
						plugin.closeSubmenu( $li , 'disabledLink' , plugin );
					}
					else{
						plugin.openSubmenu( $li , 'disabledLink' , plugin );
					}
				}
			});

		},

		initializeSubmenuToggleMouseEvents: function(){

			//Don't initialize if mouse events are disabled
			if( !this.settings.mouseEvents ) return;
			if( this.settings.clicktest ) return;
			if( this.settings.windowstest ) return;


			if( this.settings.debug ) console.log( 'initializeSubmenuToggleMouseEvents' );

			var plugin = this;

			this.$shiftnav.on( 'mouseup.shift-submenu-toggle' , '.shiftnav-submenu-activation' , function(e){ plugin.handleMouseActivation( e , this , plugin ); } );
			//$shiftnav.on( 'mouseout.shift-submenu-toggle'  , '.menu-item' , this.handleMouseout );	//now only added on mouseover
		},

		disableSubmenuToggleMouseEvents: function(){
			if( this.settings.debug ) console.log( 'disableSubmenuToggleMouseEvents' );
			$shiftnav.off( 'mouseover.shift-submenu-toggle' );
			$shiftnav.off( 'mouseout.shift-submenu-toggle'  );
		},

		
		initializeRetractors: function() {

			if( !this.settings.retractors ) return;	//Don't initialize if retractors are disabled
			var plugin = this;
			
			//set up the retractors
			this.$shiftnav.on( 'mouseup.shiftnav' , '.shiftnav-retract' , function(e){ plugin.handleSubmenuRetractorEnd( e , this, plugin); } );
		},


		initializeResponsiveToggle: function(){
			
			var plugin = this;

			//this.$toggles.on( 'click', 'a', function(e){
			this.$toggles.on( this.toggleevent, 'a', function(e){
				//allow link to be clicked but don't propagate so toggle won't activate
				e.stopPropagation();
			});

			//this.$toggles.on( 'click', function(e){
			this.$toggles.on( this.toggleevent, function(e){

				e.preventDefault();
				e.stopPropagation();
				
				//Ignore click events when toggle is disabled to avoid both touch and click events firing
				if( e.originalEvent.type == 'click' && $(this).data( 'disableToggle' ) ){
					return;
				}

				if( plugin.$shiftnav.hasClass( 'shiftnav-open-target' ) ){
					//console.log( 'close shift nav' );
					plugin.closeShiftNav();
				}
				else{
					//console.log('open shift nav');
					plugin.openShiftNav();
				}

				//Temporarily disable toggle for click event when touch is fired
				if( e.originalEvent.type != 'click' ){
					$( this ).data( 'disableToggle' , true );
					setTimeout( function(){
						$( this ).data( 'disableToggle' , false );
					}, 1000 );
				}

				return false;
								
			});

		},

		initializeSwipeHandler: function(){

			var $body = $('body'),
				start_y = 0,
				start_x = 0,
				cur_y = 0,
				cur_x = 0,
				plugin = this,
				scrollprevented = false,
				viewport_height = $(window).height(),
				$scrollPanel = this.$shiftnav.find( '.shiftnav-inner' );

			//Track where touches start
			$scrollPanel.on( 'touchstart' , function( e ){
				start_y = e.originalEvent.changedTouches[0].pageY;
				start_x = e.originalEvent.changedTouches[0].pageX;
			});

			//On drag, when at extents of scroll panel, prevent scrolling of background
			$scrollPanel.on( this.touchMove , function( e ){

				scrollprevented = false;	//keep track to maximize efficiency

				//If the ShiftNav panel is too short to scroll, prevent scrolling entirely
				//Check here because panel height can change when submenus are expanded
				if( viewport_height >= $scrollPanel[0].scrollHeight ){
					scrollprevented = true;
					e.preventDefault();
				}
				//If at top of scroll panel, prevent scrolling up
				else if( e.currentTarget.scrollTop === 0 ){
					cur_y = e.originalEvent.changedTouches[0].pageY;
					if( cur_y > start_y ){
						//console.log( 'TOP | scrolling up' );
						scrollprevented = true;
						e.preventDefault();
					}
				}
				//If at bottom of scroll panel, prevent scrolling down
				else if( e.currentTarget.scrollHeight === e.currentTarget.scrollTop + e.currentTarget.offsetHeight ){
					cur_y = e.originalEvent.changedTouches[0].pageY;
					if( cur_y < start_y ){
						//console.log( 'TOP | scrolling up' );
						scrollprevented = true;
						e.preventDefault();
					}
				}

				//If the scroll hasn't already been nuked, but
				//we're scrolling horizontally instead of vertically, stop that
				if( !scrollprevented ){
					diff_y = Math.abs( start_y - e.originalEvent.changedTouches[0].pageY );
					diff_x = Math.abs( start_x - e.originalEvent.changedTouches[0].pageX );
					if( diff_y < diff_x ){
						e.preventDefault();
					}
				}
			});

			//Swipe in the appropriate direction to close the menu
			if( shiftnav_data.swipe_close == 'on' ){

				if( this.$shiftnav.hasClass( 'shiftnav-right-edge' ) ){
					$scrollPanel.on( 'touchmove' , function( e ){
						cur_x = e.originalEvent.changedTouches[0].pageX;
						//console.log( cur_x );
						if( cur_x - start_x > plugin.settings.swipe_tolerance_x ){
							if( Math.abs( cur_y - start_y ) < plugin.settings.swipe_tolerance_y ){
								plugin.closeShiftNav();
								e.preventDefault();
							}
						}
					});
				}
				else{
					$scrollPanel.on( 'touchmove' , function( e ){
						cur_x = e.originalEvent.changedTouches[0].pageX;
						//console.log( cur_x );
						if( start_x - cur_x > plugin.settings.swipe_tolerance_x ){
							cur_y = e.originalEvent.changedTouches[0].pageY;
							if( Math.abs( cur_y - start_y ) < plugin.settings.swipe_tolerance_y ){
								plugin.closeShiftNav();
								e.preventDefault();
							}
						}
						e.stopPropagation();
					});
				}
			}

			

		},

		openShiftNav: function(){

			var plugin = this;

			$( 'body' )
				.removeClass( 'shiftnav-open-right shiftnav-open-left' )
				.addClass( this.openclass )
				.addClass( 'shiftnav-transitioning' );
				
			//console.log( 'close ' + $( '.shiftnav-open-target' ).attr( 'id' ) );
			$( '.shiftnav-open-target' ).removeClass( 'shiftnav-open-target' );
			this.$shiftnav
				.addClass( 'shiftnav-open-target' )
				.on( plugin.transitionend, function(){
						//if( plugin.settings.debug ) console.log( 'finished submenu close transition' );
						$( 'body' ).removeClass( 'shiftnav-transitioning' );
						$( this ).off( plugin.transitionend );
					});

			this.initializeTouchoffClose();
			
		},

		closeShiftNav: function(){

			var plugin = this;
			
			$( 'body' )
				.removeClass( this.openclass )
				.addClass( 'shiftnav-transitioning' );

			this.$shiftnav
				.removeClass( 'shiftnav-open-target' )
				.on( plugin.transitionend, function(){
						//if( plugin.settings.debug ) console.log( 'finished submenu close transition' );
						$( 'body' ).removeClass( 'shiftnav-transitioning' );
						$( this ).off( plugin.transitionend );
					});

			this.disableTouchoffClose();
		},

		initializeTouchoffClose: function(){

			if( !this.settings.touchOffClose ) return;  //Don't initialize if touch off close is disabled

			var plugin = this;
			$( document ).on( 'click.shiftnav ' + this.touchEnd + '.shiftnav' , function( e ){ plugin.handleTouchoffClose( e , this , plugin ); } );

		},
		disableTouchoffClose: function(){
			$( document ).off( '.shiftnav' );
		},

		handleMouseActivation: function( e , activator , plugin ){
			if( plugin.settings.debug ) console.log( 'handleMouseover, add mouseout', e );
			
			var $li = $( activator ).parent();

			if( $li.hasClass( 'shiftnav-active' ) ){
				plugin.closeSubmenu( $li , 'mouseActivate' , plugin );
			}
			else{
				plugin.openSubmenu( $li , 'mouseActivate' , plugin );
			}

			//Only attach mouseout after mouseover, this way menus opened by touch won't be closed by mouseout
			//$li.on( 'mouseout.shift-submenu-toggle' , function( e ){ plugin.handleMouseout( e , this , plugin ); } );
		},

		
		handleSubmenuRetractorEnd: function( e , li , plugin ){
			e.preventDefault();
			e.stopPropagation();

			var $li = $(li).parent( 'ul' ).parent( 'li' );
			plugin.closeSubmenu( $li , 'handleSubmenuRetractor' , plugin );

			if( plugin.settings.debug ) console.log( 'handleSubmenuRetractorEnd ' + $li.find('> a').text());

		},

		

		handleTouchoffClose: function( e , _this , plugin ){

			//Don't fire during transtion
			if( $( 'body' ).is( '.shiftnav-transitioning' ) ) return;

			if( $(e.target).parents().add( $(e.target) ).filter( '.shiftnav, .shiftnav-toggle, .shiftnav-ignore' ).size() === 0 ){


				if( plugin.settings.debug ) console.log( 'touchoff close ', e );

				e.preventDefault();
				e.stopPropagation();

				plugin.closeShiftNav();
				plugin.disableTouchoffClose();

			}

		},




		/* Controllers */
		scrollPanel: function( y ){
			if( shiftnav_data.scroll_panel == 'off' ) return 0;
			
			if( typeof y == 'undefined' ){
				return this.$shiftnav.find( '.shiftnav-inner' ).scrollTop();
			}
			else{
				this.$shiftnav.find( '.shiftnav-inner' ).scrollTop( y );
			}
		},

		openSubmenu: function( $li , tag , plugin ){
			if( !$li.hasClass( 'shiftnav-active' ) ){

				//plugin.setMinimumHeight( 'open' , $li );

				if( $li.hasClass( 'shiftnav-sub-shift' ) ){
					
					$li.siblings( '.shiftnav-active' ).removeClass( 'shiftnav-active' );
					
					//switch to position absolute, then delay activation below due to Firefox browser bug
					$li.toggleClass( 'shiftnav-caulk' );
				
					plugin.$shiftnav.addClass( 'shiftnav-sub-shift-active' );

				}
				else{
					if( plugin.settings.collapse_accordions ){
						$li.siblings( '.shiftnav-active' ).removeClass( 'shiftnav-active' );
					}
				}

				//Active flags
				$li.parents( 'ul' ).removeClass( 'shiftnav-sub-active-current' );
				$li.find( '> ul' )
					.addClass( 'shiftnav-sub-active' )
					.addClass( 'shiftnav-sub-active-current' );

				//A dumb timeout hack to fix this FireFox browser bug https://bugzilla.mozilla.org/show_bug.cgi?id=625289
				setTimeout( function(){
					$li.addClass( 'shiftnav-active' );
					$li.trigger( 'shiftnav-open-submenu' );	//API
					$li.removeClass( 'shiftnav-caulk' );

					//Wait until item has moved before calculating position
					setTimeout( function(){
						//scroll to top of the menu, make note of initial position
						var y = plugin.scrollPanel();
						$li.data( 'scroll-back' , y );
						var scrollPanelTo = $li.offset().top + y;
						plugin.scrollPanel( scrollPanelTo );
						//plugin.scrollPanel( 0 );
					}, 100 );
					
				}, 1 );
			}
		},

		closeSubmenu: function( $li , tag , plugin ){

			//var plugin = this;

			if( this.settings.debug ) console.log( 'closeSubmenu ' + $li.find( '>a' ).text() + ' [' + tag + ']' );

			//If this menu is currently active and has a submenu, close it
			if( $li.hasClass( 'menu-item-has-children' ) && $li.hasClass( 'shiftnav-active' ) ){

				$li.addClass( 'shiftnav-in-transition' );	//transition class keeps visual flag until transition completes

				$li.each( function(){
					var _$li = $(this);
					var _$ul = _$li.find( '> ul' );

					//Remove the transition flag once the transition is completed
					_$ul.on( plugin.transitionend + '_closesubmenu', function(){
						if( plugin.settings.debug ) console.log( 'finished submenu close transition' );
						_$li.removeClass( 'shiftnav-in-transition' );
						_$ul.off( plugin.transitionend  + '_closesubmenu' );
					});
				});
			}
			
			//Actually remove the active class, which causes the submenu to close
			$li.removeClass( 'shiftnav-active' );

			//Shift Sub Specific
			if( $li.hasClass( 'shiftnav-sub-shift' ) ){
				if( $li.parents( '.shiftnav-sub-shift' ).size() == 0 ) plugin.$shiftnav.removeClass( 'shiftnav-sub-shift-active' );

				//return to original position
				var y = $li.data( 'scroll-back' );
				if( y !== 'undefined' ) plugin.scrollPanel( y );
				//console.log( 'y = ' + y );

			}

			//Active flags
			$li.find( '> ul' )
				.removeClass( 'shiftnav-sub-active' )
				.removeClass( 'shiftnav-sub-active-current' );
			$li.closest( 'ul' ).addClass( 'shiftnav-sub-active-current' );

			$li.trigger( 'shiftnav-close-submenu' );	//API
			
		},

		closeAllSubmenus: function(){
			$( this.element ).find( 'li.menu-item-has-children' ).removeClass( 'shiftnav-active' );
		},

	};

	$.fn[ pluginName ] = function ( options ) {

		var args = arguments;

		if ( options === undefined || typeof options === 'object' ) {
			return this.each(function() {
				if ( !$.data( this, "plugin_" + pluginName ) ) {
					$.data( this, "plugin_" + pluginName, new Plugin( this, options ) );
				}
			});
		}
		else if ( typeof options === 'string' && options[0] !== '_' && options !== 'init') {
			// Cache the method call to make it possible to return a value
			var returns;

			this.each(function () {
				var instance = $.data(this, 'plugin_' + pluginName);

				// Tests that there's already a plugin-instance and checks that the requested public method exists
				if ( instance instanceof Plugin && typeof instance[options] === 'function') {

					// Call the method of our plugin instance, and pass it the supplied arguments.
					returns = instance[options].apply( instance, Array.prototype.slice.call( args, 1 ) );
				}

				// Allow instances to be destroyed via the 'destroy' method
				if (options === 'destroy') {
					$.data(this, 'plugin_' + pluginName, null);
				}
			});

			// If the earlier cached method gives a value back return the value, otherwise return this to preserve chainability.
			return returns !== undefined ? returns : this;
		}
	};

})( jQuery, window, document );

jQuery( document ).ready( function($){

	//Remove Loading Message
	$( '.shiftnav-loading' ).remove();

	//Scroll to non-ID "hashes"
	if( window.location.hash.substring(1,2) == '.' ){
		var $scrollTarget = $( window.location.hash.substring(1) );
		if( $scrollTarget.size() ) window.scrollTo( 0 , $scrollTarget.offset().top );
	}

	//Run ShiftNav
	jQuery( '.shiftnav' ).shiftnav({
		swipe_tolerance_x : parseInt( shiftnav_data.swipe_tolerance_x ),
		swipe_tolerance_y : parseInt( shiftnav_data.swipe_tolerance_y ),
		swipe_edge_proximity : parseInt( shiftnav_data.swipe_edge_proximity ),
		open_current : shiftnav_data.open_current == 'on' ? true : false,
		collapse_accordions : shiftnav_data.collapse_accordions == 'on' ? true : false
		//debug: true
		//mouseEvents: false
		//clicktest: true
	});

});



var shift_supports = (function() {
	var div = document.createElement('div'),
		vendors = 'Khtml Ms O Moz Webkit'.split(' ');
		

	return function(prop) {
		
		var len = vendors.length;

		if ( prop in div.style ) return true;

		prop = prop.replace(/^[a-z]/, function(val) {
			return val.toUpperCase();
		});
  
		while(len--) {
			if ( vendors[len] + prop in div.style ) {
				return true;
			}
		}
		return false;
	};
})();

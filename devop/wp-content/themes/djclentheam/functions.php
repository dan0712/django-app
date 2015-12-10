<?php


//Create a simple sub options page called 'Options'
 
if(function_exists('acf_add_options_page')) { 
 
	acf_add_options_page();
	acf_add_options_sub_page('General');
	//acf_add_options_sub_page('Opciones Página de Inicio');
 
}

/**
 * Remove admin bar

function hide_admin_bar() {
  if (is_blog_admin()) {
    return true;
  }
  return false;
}

add_filter( 'show_admin_bar', 'hide_admin_bar' );*/

/**
* Disable Feed Urls
*/
remove_action( 'wp_head', 'feed_links_extra', 3 );
remove_action( 'wp_head', 'feed_links', 2 );
remove_action( 'wp_head', 'rsd_link' );

/**
* Remove "wlwmanifest.xml" needed to enable tagging support for Windows Live Writer.
*/
remove_action('wp_head', 'wlwmanifest_link');

/**
* Remove "l10n.js" Javascript. (Pressumable used to translate phrases through javascript, robbish for me but well...
*/
wp_deregister_script('l10n');

/**
* Remove Special links for people with disabilities
*/
remove_action('wp_head', 'index_rel_link');
remove_action('wp_head', 'adjacent_posts_rel_link_wp_head', 10, 0 );
remove_action('wp_head', 'parent_post_rel_link', 10, 0 );
remove_action( 'wp_head', 'wp_shortlink_wp_head', 10, 0 );

/**
* Remove Generator */
remove_action('wp_head', 'wp_generator');

// Custom Jquery
if (!is_admin()) add_action("wp_enqueue_scripts", "my_jquery_enqueue", 11);
function my_jquery_enqueue() {
   wp_deregister_script('jquery');
   wp_register_script('jquery', "http" . ($_SERVER['SERVER_PORT'] == 443 ? "s" : "") . "://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js", false, null);
   wp_enqueue_script('jquery');
}

/**
 * Register sidebars
*/
function meir_widgets_init() {

	register_sidebar( array(
        'name' => 'Sidebar 1',
        'id' => 'sidebar_1',
        'description' => 'Sidebar 1',
        'before_widget' => '<div id="%1$s" class="%2$s">',
        'after_widget' => '</div>',
        'before_title' => '<h3  style="text-align: center;" class="widget-title">',
        'after_title' => '</h3>',
    ) );
	
	register_sidebar( array(
        'name' => 'Main Sidebar',
        'id' => 'main_sidebar',
        'description' => 'Main Sidebar',
        'before_widget' => '<div id="%1$s" class="widget %2$s">',
        'after_widget' => '</div>',
        'before_title' => '<h3 class="widget-title">',
        'after_title' => '</h3>',
    ) );



}

add_action( 'widgets_init', 'meir_widgets_init' );

// Register main menus
	function register_menu() {
	register_nav_menus( array(
	'header_menu' => 'Primary Menu',
	'footer_menu' => 'Footer Menu',
	'shop_menu' => 'Shop Menu',
	) );
	}

	add_action( 'init' , 'register_menu' );

// Support for post thumbnail
add_theme_support( 'post-thumbnails' );

// Remove filters from excerpt
remove_all_filters('the_excerpt');


// Support for woocommerce
add_theme_support( 'woocommerce' );



function custom_comment_layout($comment, $args, $depth) {
   $GLOBALS['comment'] = $comment; ?>
   <li <?php comment_class(); ?> id="li-comment-<?php comment_ID() ?>">
     <div id="comment-<?php comment_ID(); ?>">
      <?php echo get_avatar($comment,$size='48' ); ?>

      <?php if ($comment->comment_approved == '0') : ?>
         <em><?php _e('Your comment is awaiting moderation.') ?></em>
         <br />
      <?php endif; ?>
 
      <div class="comment-meta commentmetadata">
          <?php printf(__('<cite class="fn">%s</cite>'), get_comment_author_link()) ?> / <a href="<?php echo htmlspecialchars( get_comment_link( $comment->comment_ID ) ) ?>">
              <?php printf(__('%1$s'), get_comment_date()) ?>
          </a>
          <?php edit_comment_link(__(' (Edit)'),'  ','') ?>
          
          <div class="the_comment"><?php comment_text() ?></div>
      </div>
      
      <div class="clear"></div>
 

      <!--<div class="reply">
         <?php comment_reply_link(array_merge( $args, array('depth' => $depth, 'max_depth' => $args['max_depth']))) ?>
      </div>-->
     </div>
<?php
        }
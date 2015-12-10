<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<!--[if IE 7]><html lang="en" class="ie7"><![endif]-->
<!--[if IE 8]><html lang="en" class="ie8"><![endif]-->
<!--[if IE 9]><html lang="en" class="ie9"><![endif]-->
<!--[if (gt IE 9)|!(IE)]><html lang="en"><![endif]-->
<!--[if !IE]><html lang="en"><![endif]-->
<head>
	<meta charset="<?php bloginfo('charset'); ?>" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
	<script src="<?php bloginfo('template_directory')?>/assets/js/lib/modernizr.js"></script>

	<title><?php wp_title( '|', true, 'right' ); bloginfo( 'name' ); ?></title>
	
	<!-- Fonts -->
	<link href='http://fonts.googleapis.com/css?family=Raleway:400,100,300,700' rel='stylesheet' type='text/css'>
	<link href='http://fonts.googleapis.com/css?family=Open+Sans:400,700,400italic,700italic' rel='stylesheet' type='text/css'>

	<!-- Essential stylesheets -->
	<!--<link rel="stylesheet" href="<?php bloginfo('template_directory')?>/assets/css/lib/font-awesome.min.css">-->
    <link rel="stylesheet" href="http://cdn.jsdelivr.net/fontawesome/4.3.0/css/font-awesome.min.css?ver=4.3.0">
    
	<link rel="stylesheet" href="<?php bloginfo('template_directory')?>/assets/css/lib/magnific-popup.css">
	<link rel="stylesheet" href="<?php bloginfo('template_directory')?>/assets/css/lib/bxslider.css">
	<link rel="stylesheet" href="<?php bloginfo('template_directory')?>/assets/css/lib/owl.carousel.css">
	<link rel="stylesheet" href="<?php bloginfo('template_directory')?>/assets/css/lib/owl.theme.css">
	<link rel="stylesheet" href="<?php bloginfo('template_directory')?>/assets/css/lib/base.css">

	<!-- The stylesheet -->
	<link rel="stylesheet" href="<?php bloginfo('template_directory')?>/assets/css/style.css">
	<!--<link rel="stylesheet" href="css/color/green.css">-->
    <link rel="stylesheet" href="<?php bloginfo('template_directory')?>/assets/css/custom.css">
    <link rel="stylesheet" href="<?php bloginfo('template_directory')?>/assets/css/main.css">
    <link rel="stylesheet" href="<?php bloginfo('template_directory')?>/assets/css/blog.css">

	<!-- The favicon -->
	
	<?php $theme_favicon = get_field('theme_favicon', 'option'); ?>
    <?php if($theme_favicon  != ""): ?>
    	<link rel="shortcut icon" href="<?php echo $theme_favicon; ?>">
    <?php endif; ?>
    
    <?php wp_head(); ?>
	<!-- Javascript -->
	<!--<script src="<?php bloginfo('template_directory')?>/assets/js/lib/jquery.min.js"></script>-->
    
    <script src="<?php bloginfo('template_directory')?>/assets/js/nt-shortcode.js"></script>
	<script src="<?php bloginfo('template_directory')?>/assets/js/lib/retina.min.js"></script>
	<script src="<?php bloginfo('template_directory')?>/assets/js/lib/jquery.magnific-popup.min.js"></script>
	<script src="<?php bloginfo('template_directory')?>/assets/js/lib/jquery.bxslider.min.js"></script>
	<!--<script src="<?php bloginfo('template_directory')?>/assets/js/lib/owl.carousel.min.js"></script>-->
	<script src="<?php bloginfo('template_directory')?>/assets/js/lib/jquery.fitvids.js"></script>
	<script src="<?php bloginfo('template_directory')?>/assets/js/lib/jquery.equal.js"></script>
	<script src="<?php bloginfo('template_directory')?>/assets/js/main.js"></script>
	<!--[if lt IE 9]>
		<script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
	<![endif]-->
<style type="text/css">
body,blockquote small,.o-hover em{font-family:'Open Sans';}
h1,h2,h3,h4,h5,h6,.h1,.h2,.h3,.h4,.h5,.h6,.uber,.btn,button,input[type="submit"],a.arrow-link,.o-hover span,.menu,.icon-nav b,.menu{font-family:'Raleway';}
</style>
<style type="text/css" id="pe-theme-custom-colors">
.text-color{color:#bce550;}
.btn.outline.color{color:#bce550;}
a.arrow-link:hover{color:#bce550;}
a.arrow-link:hover:before{color:#bce550;}
.service-item:hover>i{color:#bce550;}
.service-item:hover>a.arrow-link:before{color:#bce550;}
.c-details a:hover{color:#bce550;}
.c-details a:hover i{color:#bce550;}
a.btn:hover{background-color:#bce550;}
button:hover{background-color:#bce550;}
input[type='submit']:hover{background-color:#bce550;}
a .icon:hover{background-color:#bce550;}
.icon-nav a:hover>i{background-color:#bce550;}
a>.back-top{background-color:#bce550;}
a >.back-top{background-color:#bce550;background-color:rgba(163, 199, 69, 0.85);}
a.btn.outline:hover{background-color:#bce550;}
button.outline:hover{background-color:#bce550;}
input[type='submit'].outline:hover{background-color:#bce550;}
.btn.color{background-color:#bce550;}
* .btn.outline.color{background-color:#bce550;}
* a.btn.outline:hover{border-color:#bce550;}
* button.outline:hover{border-color:#bce550;}
* input[type='submit'].outline:hover{border-color:#bce550;}
/* Accordion */
.nt-nt_accordions-wrap {  }
.nt-nt_accordions-wrap .tab { cursor: pointer;  }
.nt-nt_accordions-wrap .tab i { }
.nt-nt_accordions-wrap .tab .nt-icon-minus { display: none; }
.nt-nt_accordions-wrap .tab .nt-icon-plus { display: inline; }
.nt-nt_accordions-wrap .tab.current .nt-icon-minus { color:#A6CE39; display: inline; }
.nt-nt_accordions-wrap .tab.current .nt-icon-plus { color:#A6CE39; display: none; }
.nt-nt_accordions-wrap .pane { display: none; }
.nt-nt_accordions-wrap .tab .nt-icon-minus:after {
color:#A6CE39;
}
</style>
</head>


<body <?php body_class(); ?>>



	<!-- Top of the page -->
	<div id="top"></div>

	<!-- Top bar -->
	<div class="top-bar tb-large">
		<div class="row">
			<div class="twelve col">


				<!-- Symbolic or typographic logo -->
				<div class="tb-logo">
                    <?php $logo = get_field('theme_logo', 'option'); ?>
					<?php if($logo  != ""): ?>
                        <a href="#home" class="scrollto">
                            <img src="<?php echo $logo; ?>" alt="logo" />
                        </a>
                    <?php endif; ?>
				</div>


				<!-- Menu toggle -->
				<input type="checkbox" id="toggle" />
				<label for="toggle" class="toggle"></label>


				<!-- Menu items -->
				<nav class="menu">
					<?php wp_nav_menu( array('theme_location' => 'header_menu', 'container' => 'false', 'items_wrap' => '<ul id="%1$s" class="header_menu menu %2$s">%3$s</ul>')); ?>
				</nav>


			</div>
		</div>
	</div>
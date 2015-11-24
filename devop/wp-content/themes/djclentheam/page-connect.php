<?php
/**
 * Template Name:  Connect Page Template
 * Description: Connect Page
 */
get_header(); ?>
<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
}

.form-field {
    color: #333;
}

p {
    margin-top: 0;
    margin-bottom: 10px;
    font-family: 'Raleway', 'Open Sans', Helvetica, Arial, sans-serif;
    font-size: 16px;
    line-height: 1.5;
}

p.errors {
    padding: 5px;
    background-color: #e88;
    color: #fff;
}

p.error.no-label {
    position: relative;
    top: -6px;
    color: #aa0000;
}

p.error input {
    background-color: #fff6f6;
}

label {
    display: block;
}

.form-field.required label {
    font-weight: bold;
}

.form-field.required label:after {
    content: '*';
}

input, select {
    -webkit-appearance: none;
    width: 100%;
    min-height: 15px;
    padding: 5px 10px;
    background-color: #fff;
    border: solid 2px #bbb;
    border-radius: 0;
    outline: none;
    font-size: 16px;
    line-height: 18px;
    color: #888;
}

input:focus {
    outline: none;
}

.submit input {
    width: 110px;
    margin-top: 15px;
    padding: 12px 25px;
    background-color: #3a81d3;
    border: none;
    border-radius: 0;
    font-weight: bold;
    text-transform: uppercase;
    color: #fff;
    cursor: pointer;
    -webkit-transition: all .2s;
    -moz-transition: all .2s;
    -ms-transition: all .2s;
    -o-transition: all .2s;
    transition: all .2s;
}

.submit input:hover, .submit input:active {
    background-color: #529e00;
}

@media all and (min-width: 769px) {
    form {
        width: 50%;
        margin: 0 auto;
    }
}
</style>
<?php if (have_posts()) : while (have_posts()) : the_post(); ?>


<div id="connect" class="pagebuilder-content">

<section class="padding-top-normal padding-bottom-normal  bg-image-cover section-type-intro" id="section-1" style="background-color: #fff;background-image: url('<?php the_field('section_1_bg'); ?>');">

	
    <div class="row section-content">
    
        <div class="eight col center text-center">
        
            <div class="intro-section-content section-content-wrap">
            
            	<?php the_field('section_1_content'); ?>
                
            
                <div class="row">
                
                <?php if(get_field('section_1_content_2')): while(has_sub_field('section_1_content_2')): ?>
                <div class="six columns col">
                
                	<?php the_sub_field('section_1_sub_content'); ?>
                    
                
                </div>
                <?php endwhile; endif; ?>
 
                
                </div>
            
            </div>
        
        </div>
    
    </div>

	
	
</section>


<section class="padding-top-normal padding-bottom-normal  section-type-column" style="background-color: <?php the_field('section_2_bg_color'); ?>;" id="section-form-sign-up">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	<?php the_field('section_2_content'); ?>
                
            
            </div>
        
        </div>
    
    </div>

</section>

<section class="padding-top-normal padding-bottom-normal  section-type-column" style="background-color: <?php the_field('section_3_bg_color'); ?>;" id="section-form-schedule-demo">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	
                <?php the_field('section_3_content'); ?>
                
            
            </div>
        
        </div>
    
    </div>

</section>

<section class="padding-top-normal padding-bottom-large text-color-light section-type-column" style="background-color: #a6ce39;" id="section-5">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	
                <?php if ( !function_exists('dynamic_sidebar')|| !dynamic_sidebar('sidebar_1') ) : endif; ?>
            
            </div>
        
        </div>
    
    </div>

</section>

</div>


<?php endwhile; endif; ?>

<?php get_footer(); ?>
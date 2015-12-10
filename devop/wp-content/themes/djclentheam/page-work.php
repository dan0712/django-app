<?php
/**
 * Template Name:  Work Page Template
 * Description: Work Page
 */
get_header(); ?>

<?php if (have_posts()) : while (have_posts()) : the_post(); ?>

<div id="team" class="pagebuilder-content">

<section class="padding-top-large padding-bottom-large  bg-image-cover section-type-intro" id="section-1" style="background-color: #fff;background-image: url('<?php the_field('section_1_bg'); ?>');">

	
	
		<div class="row section-content">
			<div class="eight col center text-center">
				<div class="intro-section-content section-content-wrap">
                
                	<?php the_field('section_1_content'); ?>
                    
				</div>
			</div>
		</div>

	
	
</section>

<section class="padding-top-none padding-bottom-none text-color-light section-type-column" style="background-color: <?php the_field('section_2_bg_color'); ?>;" id="section-27">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            <?php the_field('section_2_content'); ?>
            
           
            
            </div>
        
        </div>
    
    </div>

</section>

<section class="padding-top-normal padding-bottom-large  section-type-column" style="background-color: <?php the_field('section_3_bg_color'); ?>;" id="section-10">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
                <?php the_field('section_3_content'); ?>
                
               
            
            </div>
        
        </div>
    
    </div>

</section>

<section class="padding-top-normal padding-bottom-none  section-type-column" style="background-color: <?php the_field('section_4_bg_color'); ?>;" id="section-14">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
                <?php the_field('section_4_content'); ?>
                
                
            
            </div>
        
        </div>
    
    </div>

</section>

<section class="padding-top-none padding-bottom-large  section-type-column" style="background-color: <?php the_field('section_5_bg_color'); ?> ;" id="section-19">

    <div class="container">
    
        <div class="row">
        
        
        <?php if(get_field('section_5_content')): while(has_sub_field('section_5_content')): ?>
               
                
            <div class="six columns col">
            
                <?php the_sub_field('section_5_sub_content'); ?>
            
            </div>
            
        <?php endwhile; endif; ?>

        </div>
    
    </div>

</section>

<section class="padding-top-normal padding-bottom-none  section-type-column" style="background-color: <?php the_field('section_6_bg_color'); ?>;" id="section-12">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
                <?php the_field('section_6_content'); ?>
                
                
            
            </div>
        
        </div>
    
    </div>

</section>

<section class="padding-top-none padding-bottom-large  section-type-column" style="background-color: <?php the_field('section_7_bg_color'); ?>;" id="section-16">

    <div class="container">
    
        <div class="row">

            
				<?php if(get_field('section_7_content')): while(has_sub_field('section_7_content')): ?>
                   
                    
                    <div class="six columns col">
                    
                        <?php the_sub_field('section_7_sub_content'); ?>
                    
                    </div>
                
                <?php endwhile; endif; ?>
            
        
        </div>
    
    </div>

</section>

<section class="padding-top-large padding-bottom-large text-color-light section-type-column" style="background-color: #a6ce39;" id="section-22">

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
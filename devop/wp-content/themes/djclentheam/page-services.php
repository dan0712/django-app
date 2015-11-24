<?php
/**
 * Template Name:  Services Page Template
 * Description: Services Page
 */
get_header(); ?>

<?php if (have_posts()) : while (have_posts()) : the_post(); ?>

<div id="tools" class="pagebuilder-content">
<section class="padding-top-large padding-bottom-large  bg-image-cover section-type-intro" id="section-26" style="background-color: #fff;background-image: url('<?php the_field('section_1_bg'); ?>');">

	
	
		<div class="row section-content">
			<div class="eight col center text-center">
				<div class="intro-section-content section-content-wrap">
                
                	<?php the_field('section_1_content'); ?>
                    
                
                </div>
			</div>
		</div>

	
	
</section>


<section class="padding-top-none padding-bottom-none text-color-light section-type-column" style="background-color: <?php the_field('section_2_bg_color'); ?>;" id="section-28">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            
            <?php the_field('section_2_content'); ?>
            
            </div>
        
        </div>
    
    </div>

</section>

<section class="padding-top-large padding-bottom-large  section-type-column" style="background-color: <?php the_field('section_3_bg_color'); ?>;" id="section-5">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	
                
                <?php the_field('section_3_content'); ?>
            
            </div>
        
        </div>
    
    </div>

</section>

<section class="padding-top-normal padding-bottom-normal  section-type-column" style="background-color:<?php the_field('section_4_bg_color'); ?>;" id="section-33">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
                <div class="row">
                
                    <div class="nine columns col center">
                    
                    	
                        <?php echo do_shortcode('[owl-carousel category="Tools" singleItem="true" autoPlay="true" navigation="true"]'); //the_field('section_4_content'); ?>
                    
                    </div>
                
                </div>
            
            </div>
        
        </div>
    
    </div>

</section>


<section class="padding-top-normal padding-bottom-none  bg-image-cover section-type-process" id="section-35" style="background-color: <?php the_field('section_5_bg_color'); ?>;">
	
		<div class="row equal">

			
				
				<?php if(get_field('section_5_content')): while(has_sub_field('section_5_content')): ?>
                
                <div class="col four">
					<div class="icon-circle">

						
							<i class="fa <?php the_sub_field('section_5_icon_type'); ?>"></i>

							
                            <?php the_sub_field('section_5_sub_content'); ?>

					</div>
				</div>
                
                <?php endwhile; endif; ?>
	
		</div>

	
</section>

<section class="padding-top-none padding-bottom-normal  section-type-column" style="background-color:  <?php the_field('section_6_bg_color'); ?>;" id="section-51">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	
                
                <?php the_field('section_6_content'); ?>
            
            </div>
        
        </div>
    
    </div>

</section>

<section class="padding-top-normal padding-bottom-normal  section-type-column" style="background-color: <?php the_field('section_7_bg_color'); ?>;" id="section-14">


    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	<?php the_field('section_7_content'); ?>
                
            
            </div>
        
        </div>
    
    </div>

</section>


<section class="padding-top-normal padding-bottom-none  bg-image-cover section-type-process" id="section-39" style="background-color: <?php the_field('section_8_bg_color'); ?>;">

	
	
		<div class="row section-content">
			<div class="eight col center text-center">
				<div class="section-content-wrap">
                
                	<?php the_field('section_8_content'); ?>
                    
				</div>
			</div>
		</div>

	
	
	
		<div class="row equal">

			
				
				<?php if(get_field('section_8_content_2')): while(has_sub_field('section_8_content_2')): ?>
                
                <div class="col three medium-six small-twelve">
					<div class="icon-circle">

						
							<i class="fa <?php the_sub_field('section_8_icon_type'); ?>"></i>

							<?php the_sub_field('section_8_sub_content'); ?>
						
					</div>
				</div>
                
                <?php endwhile; endif; ?>
			
		</div>

	
</section>

<section class="padding-top-none padding-bottom-normal  section-type-column" style="background-color: #f0f3f7;" id="section-49">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	
                <?php the_field('section_8_content_3'); ?>
                
            
            </div>
        
        </div>
    
    </div>

</section>


<section class="padding-top-large padding-bottom-large text-color-light bg-image-cover section-type-process" id="section-30" style="background-color: #fff;background-image: url('<?php the_field('section_9_bg'); ?>');">

	
	
		<div class="row section-content">
			<div class="eight col center text-center">
				<div class="section-content-wrap">
                
                	<?php the_field('section_9_content'); ?>
                
                </div>
			</div>
		</div>

	
	
	
		<div class="row equal">

			
				
				<?php if(get_field('section_9_content_2')): while(has_sub_field('section_9_content_2')): ?>

                <div class="col six">
					<div class="icon-circle">

						
							<i class="fa <?php the_sub_field('section_9_icon_type'); ?>"></i>

							<?php the_sub_field('section_9_sub_content'); ?>

					</div>
				</div>
                <?php endwhile; endif; ?>
			
		</div>

	
</section>



<section class="padding-top-large padding-bottom-large text-color-light section-type-column" style="background-color: #a6ce39;" id="section-21">

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
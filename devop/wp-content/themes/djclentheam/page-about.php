<?php
/**
 * Template Name:  About Page Template
 * Description: About	 Page
 */
get_header(); ?>

<?php if (have_posts()) : while (have_posts()) : the_post(); ?>


<div id="features" class="pagebuilder-content">
<section class="padding-top-normal padding-bottom-normal  bg-image-cover section-type-intro" id="section-24" style="background-color: #fff;background-image: url('<?php the_field('section_1_bg'); ?>');">

	
	
		<div class="row section-content">
			<div class="eight col center text-center">
				<div class="intro-section-content section-content-wrap">
                
                
                <?php the_field('section_1_content'); ?>
                
                </div>
			
            </div>
		</div>

	
	
		<div class="row equal">

			
				<?php if(get_field('section_1_content_2')): while(has_sub_field('section_1_content_2')): ?>
				<div class="col four">
					<div class="icon-nav">

                        <i class="fa <?php the_sub_field('section_1_icon_type'); ?>"></i>
                        
                        <?php the_sub_field('section_1_sub_content'); ?>
	
						
					</div>
				</div>
                <?php endwhile; endif; ?>


			
		</div>

	
</section>


<section class="padding-top-none padding-bottom-none text-color-light section-type-column" style="background-color: <?php the_field('section_2_bg_color'); ?>;" id="section-46">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	
                
                <?php the_field('section_2_content'); ?>
            
            </div>
        
        </div>
    
    </div>

</section>



<section class="padding-top-normal padding-bottom-none  bg-image-cover section-type-process" id="section-41" style="background-color:<?php the_field('section_3_bg_color'); ?>;">

	
	
		<div class="row section-content">
			<div class="eight col center text-center">
				<div class="section-content-wrap">
                
                
					<?php the_field('section_3_content'); ?>

				</div>
			</div>
		</div>

	
	
	
		<div class="row equal">

			
				<?php if(get_field('section_3_content_2')): while(has_sub_field('section_3_content_2')): ?>
				<div class="col three medium-six small-twelve">
					<div class="icon-circle">

						
							<i class="fa <?php the_sub_field('section_3_icon_type'); ?>"></i>

						
							<?php the_sub_field('section_3_sub_content'); ?>
							

						
					</div>
				</div>
                <?php endwhile; endif; ?>
		
		</div>

	
</section>

<section class="padding-top-none padding-bottom-large  section-type-column" style="background-color: <?php the_field('section_4_bg_color'); ?>;" id="section-59">

    <div class="container">
    
        <div class="row">
        
            <div class="three columns col"></div>
            
            <div class="three columns col">
            
            	
                
                <?php the_field('section_4_content_1'); ?>
            
            </div>
            
            <div class="three columns col">
            
            	
                
                <?php the_field('section_4_content_2'); ?>
            
            </div>
            
            <div class="three columns col"></div>
        
        </div>
    
    </div>

</section>




<section class="padding-top-normal padding-bottom-normal  bg-image-cover section-type-process" id="section-centralized-advisor-dashboard" style="background-color: #fff;background-image: url('<?php the_field('section_5_bg'); ?>');">

	
	
		<div class="row section-content">
			<div class="eight col center text-center">
				<div class="section-content-wrap">
                
                	<?php the_field('section_5_content'); ?>
                
				</div>
			</div>
		</div>

	
	
	
		<div class="row equal">

			
				
				<?php if(get_field('section_5_content_2')): while(has_sub_field('section_5_content_2')): ?>

                <div class="col four">
					<div class="icon-circle">

                            <i class="fa <?php the_sub_field('section_5_icon_type'); ?>"></i>

						
							<?php the_sub_field('section_5_sub_content'); ?>

					</div>
				</div>
                <?php endwhile; endif; ?>

		</div>

	
</section>


<section class="padding-top-normal padding-bottom-normal  bg-image-cover section-type-process" id="section-taxes" style="background-color: <?php the_field('section_6_bg_color'); ?>;">

	
	
		<div class="row section-content">
			<div class="eight col center text-center">
				<div class="section-content-wrap">
                
                	<?php the_field('section_6_content'); ?>

				</div>
			</div>

		</div>

	
	
	
		<div class="row equal">

			
				<?php if(get_field('section_6_content_2')): while(has_sub_field('section_6_content_2')): ?>
                
				<div class="col six">
					<div class="icon-circle">

						
							<i class="fa <?php the_sub_field('section_6_icon_type'); ?>"></i>

							<?php the_sub_field('section_6_sub_content'); ?>
						
					</div>
				</div>
                
                <?php endwhile; endif; ?>

			
		</div>

	
</section>

<section class="padding-top-none padding-bottom-none  section-type-column" style="background-color: <?php the_field('section_7_bg_color'); ?> ;" id="section-64">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	
                <?php the_field('section_7_content'); ?>
                
            
            </div>
        
        </div>
    
    </div>

</section>


<section class="padding-top-normal padding-bottom-large  section-type-column" style="background-color: <?php the_field('section_8_bg'); ?>;" id="section-20">

    <div class="container">
    
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	<?php the_field('section_8_content'); ?>
            
            </div>
            
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
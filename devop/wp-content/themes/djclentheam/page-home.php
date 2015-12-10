<?php
/**
 * Template Name:  Home Page Template
 * Description: Home Page
 */
get_header(); ?>

<?php if (have_posts()) : while (have_posts()) : the_post(); ?>


	<!-- Home static background -->
	<div id="home-page" class="pagebuilder-content">

<section class="padding-top-large padding-bottom-large  bg-image-cover section-type-intro" id="section-intro" style="background-color: #fff;background-image: url('<?php the_field('section_1_bg'); ?>');">

	
	
		<div class="row section-content">
			<div class="eight col center text-center">
				<div class="intro-section-content section-content-wrap">

                <?php the_field('section_1_content'); ?>
                
                </div>
			</div>
		</div>

	
	
</section>


<section class="padding-top-none padding-bottom-none text-color-light section-type-column" style="background-color: <?php the_field('section_2_bg_color'); ?>;" id="section-63">

    <div class="container">
        <div class="row">
            <div class="twelve columns col">
            
            <?php the_field('section_2_content'); ?>
            
            </div>
        </div>
    </div>
</section>


<section class="padding-top-normal padding-bottom-normal  section-type-column" style="background-color: <?php the_field('section_3_bg_color'); ?>;" id="section-about">
    <div class="container">
        <div class="row">
            <div class="twelve columns col">
            	
                <?php the_field('section_3_content'); ?>
            
            </div>
        </div>
    </div>
</section>

<section class="padding-top-large padding-bottom-none  bg-image-cover section-type-process" id="section-48" style="background-color: <?php the_field('section_4_bg_color'); ?>;">

		<div class="row equal">

				<?php if(get_field('section_4_content')): while(has_sub_field('section_4_content')): ?>

                <div class="col four">
					<div class="icon-circle">
							<i class="fa <?php the_sub_field('section_4_icon_type'); ?>"></i>
							
                            <?php the_sub_field('section_4_sub_content'); ?>
					</div>
				</div>
                <?php endwhile; endif; ?>

		</div>

	
</section>


<section class="padding-top-none padding-bottom-large  section-type-column" style="background-color: <?php the_field('section_5_bg_color'); ?>;" id="section-51">
    <div class="container">
        <div class="row">
        
            <div class="twelve columns col">
            	
                <?php the_field('section_5_content'); ?>
            	
            
            </div>
        </div>
    </div>

</section>


<section class="padding-top-normal padding-bottom-normal  bg-image-cover section-type-process" id="section-66" style="background-color: <?php the_field('section_6_bg_color'); ?>;">

	
	
		<div class="row section-content">
			<div class="eight col center text-center">
				<div class="section-content-wrap">
                
                	<?php the_field('section_6_content'); ?>
                    
					
                </div>
			</div>
		</div>


	
		<div class="row equal">

				<?php if(get_field('section_7_content')): while(has_sub_field('section_7_content')): ?>
				
				<div class="col four">
					<div class="icon-circle">

                            <i class="fa <?php the_sub_field('section_7_icon_type'); ?>"></i>

						
							<?php the_sub_field('section_7_sub_content'); ?>
							

						
					</div>
				</div>
				<?php endwhile; endif; ?>

			
		</div>

	
</section>


<section class="padding-top-normal padding-bottom-normal text-color-light section-type-column" style="background-color:<?php the_field('section_8_bg_color'); ?>;background-image: url('<?php the_field('section_8_bg'); ?>');" id="section-fast-and-painless">

<div class="container">

<div class="row">

    <div class="twelve columns col">
    
    <?php the_field('section_8_content'); ?>
    
    
    </div>

</div>

</div>

</section>

<section class="padding-top-normal padding-bottom-none  bg-image-cover section-type-process" id="section-70" style="background-color: <?php the_field('section_9_bg_color'); ?>;">

	
	
	
	
		<div class="row equal">

			
				<?php if(get_field('section_9_content')): while(has_sub_field('section_9_content')): ?>
			
				<div class="col four">
					<div class="icon-circle">

						
							<i class="fa <?php the_sub_field('section_9_icon_type'); ?>"></i>

                            
                            <?php the_sub_field('section_9_sub_content'); ?>

						
					</div>
				</div>
                <?php endwhile; endif; ?>


			
		</div>

	
</section>

<section class="padding-top-large padding-bottom-large  section-type-column" style="background-color:<?php the_field('section_10_bg_color'); ?>;background-image: url('<?php the_field('section_10_bg'); ?>');" id="section-53">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
                <div class="nine center columns col">
                
                <?php the_field('section_10_content'); ?>

                </div>
            
            </div>
        
        </div>
    
    </div>

</section>


<section class="padding-top-normal padding-bottom-large  section-type-column" style="background-color: <?php the_field('section_11_bg_color'); ?>;" id="section-press">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
                <div class="row">
                
                    <div class="eight columns col center">
                    
                    	<?php the_field('section_11_content'); ?>

                    </div>
                
                
                </div>
                
            </div>
        
        </div>
    
    </div>

</section>


<section class="padding-top-large padding-bottom-none text-color-light section-type-column" style="background-color: <?php the_field('section_12_bg_color'); ?>#a6ce39;" id="section-58">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
                <div class="row">
                
                    <div class="nine columns col center">
                        
                        <div class="row">
                            
                            
                            <?php if(get_field('section_12_content')): while(has_sub_field('section_12_content')): ?>
                            <div class="four columns col">
                                <?php the_sub_field('section_12_sub_content'); ?>
                                
                            </div>
                            <?php endwhile; endif; ?>
                           
                        
                        </div>
                    
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<section class="padding-top-normal padding-bottom-large text-color-light section-type-column" style="background-color: #a6ce39;" id="section-22">

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
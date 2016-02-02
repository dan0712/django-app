<?php
/**
 * Template Name:  FAQ Page Template
 * Description: FAQ Page
 */
get_header(); ?>

<?php if (have_posts()) : while (have_posts()) : the_post(); ?>



<div id="frequently-asked-questions" class="pagebuilder-content">


<section class="padding-top-large padding-bottom-large text-color-light bg-image-cover section-type-intro" id="section-1" style="background-color: #fff;background-image: url('<?php the_field('section_1_bg'); ?>');">

	
</section>

<section class="padding-top-none padding-bottom-none text-color-light section-type-column" style="background-color: <?php the_field('section_2_bg_color'); ?>;" id="section-3">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            <?php the_field('section_2_content'); ?>
            
            
            
            </div>
        
        </div>
    
    </div>

</section>

<section class="padding-top-normal padding-bottom-none  section-type-column" style="background-color: <?php the_field('section_3_bg_color'); ?>;" id="section-topics">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	<?php the_field('section_3_content'); ?>
                
            
            </div>
        
        </div>
    
    </div>

</section>

<section class="padding-top-none padding-bottom-normal  section-type-column" style="background-color: <?php the_field('section_4_bg_color'); ?>;" id="section-18">

    <div class="container">
    
        <div class="row">
        
            <?php if(get_field('section_4_content')): while(has_sub_field('section_4_content')): ?>
                
            <div class="six columns col">
            
                <?php the_sub_field('section_4_sub_content'); ?>
                
             
             </div>
             <?php endwhile; endif; ?>
        
        </div>
    
    </div>

</section>

<section class="padding-top-normal padding-bottom-normal  section-type-column" style="background-color: <?php the_field('section_5_bg_color'); ?>;" id="section-betasmartz-institutional-overview">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	<h2 style="text-align: center;"><?php the_field('section_5_title'); ?></h2>
            
                <div class="nt-nt_accordions-wrap" data-active="0">
                
                    <?php if(get_field('section_5_content')): while(has_sub_field('section_5_content')): ?>
                    <div class="tab">
                    
                        <i class="nt-icon-plus"></i><i class="nt-icon-minus"></i> <?php the_sub_field('section_5_sub_title'); ?>
                    
                    </div>
                
                    <div class="pane clearfix">
                    
                    	<?php the_sub_field('section_5_sub_content'); ?>
                        
                    
                    </div>
                    <?php endwhile; endif; ?>
                
                </div>
            	
                <h5><a href="#section-topics" class="button">Back to Top</a></h5>
            
            </div>
        
        </div>
    
    </div>

</section>


<section class="padding-top-normal padding-bottom-normal  section-type-column" style="background-color: <?php the_field('section_6_bg_color'); ?>;" id="section-accounts-and-access">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	<h2 style="text-align: center;"><?php the_field('section_6_title'); ?></h2>
            
                <div class="nt-nt_accordions-wrap" data-active="0">
                
                    <?php if(get_field('section_6_content')): while(has_sub_field('section_6_content')): ?>
                    <div class="tab">
                    
                        <i class="nt-icon-plus"></i><i class="nt-icon-minus"></i> <?php the_sub_field('section_6_sub_title'); ?>
                    
                    </div>
                
                    <div class="pane clearfix">
                    
                    	<?php the_sub_field('section_6_sub_content'); ?>
                        
                    
                    </div>
                    <?php endwhile; endif; ?>
                
                </div>
            	
                <h5><a href="#section-topics" class="button">Back to Top</a></h5>
            
            </div>
        
        </div>
    
    </div>

</section>

<section class="padding-top-normal padding-bottom-normal  section-type-column" style="background-color: <?php the_field('section_7_bg_color'); ?>;" id="section-pricing-and-fees">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	<h2 style="text-align: center;"><?php the_field('section_7_title'); ?></h2>
            
                <div class="nt-nt_accordions-wrap" data-active="0">
                
                    <?php if(get_field('section_7_content')): while(has_sub_field('section_7_content')): ?>
                    <div class="tab">
                    
                        <i class="nt-icon-plus"></i><i class="nt-icon-minus"></i> <?php the_sub_field('section_7_sub_title'); ?>
                    
                    </div>
                
                    <div class="pane clearfix">
                    
                    	<?php the_sub_field('section_7_sub_content'); ?>
                        
                    
                    </div>
                    <?php endwhile; endif; ?>
                
                </div>
            	
                <h5><a href="#section-topics" class="button">Back to Top</a></h5>
            
            </div>
        
        </div>
    
    </div>

</section>


<section class="padding-top-normal padding-bottom-normal  section-type-column" style="background-color: <?php the_field('section_8_bg_color'); ?>;" id="section-deposits-withdrawals-transfers">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	<h2 style="text-align: center;"><?php the_field('section_8_title'); ?></h2>
            
                <div class="nt-nt_accordions-wrap" data-active="0">
                
                    <?php if(get_field('section_8_content')): while(has_sub_field('section_8_content')): ?>
                    <div class="tab">
                    
                        <i class="nt-icon-plus"></i><i class="nt-icon-minus"></i> <?php the_sub_field('section_8_sub_title'); ?>
                    
                    </div>
                
                    <div class="pane clearfix">
                    
                    	<?php the_sub_field('section_8_sub_content'); ?>
                        
                    
                    </div>
                    <?php endwhile; endif; ?>
                
                </div>
            	
                <h5><a href="#section-topics" class="button">Back to Top</a></h5>
            
            </div>
        
        </div>
    
    </div>

</section>


<section class="padding-top-large padding-bottom-large  section-type-column" style="background-color: <?php the_field('section_9_bg_color'); ?>;" id="section-custody-clearing-trading">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	<h2 style="text-align: center;"><?php the_field('section_9_title'); ?></h2>
            
                <div class="nt-nt_accordions-wrap" data-active="0">
                
                    <?php if(get_field('section_9_content')): while(has_sub_field('section_9_content')): ?>
                    <div class="tab">
                    
                        <i class="nt-icon-plus"></i><i class="nt-icon-minus"></i> <?php the_sub_field('section_9_sub_title'); ?>
                    
                    </div>
                
                    <div class="pane clearfix">
                    
                    	<?php the_sub_field('section_9_sub_content'); ?>
                        
                    
                    </div>
                    <?php endwhile; endif; ?>
                
                </div>
            	
                <h5><a href="#section-topics" class="button">Back to Top</a></h5>
            
            </div>
        
        </div>
    
    </div>

</section>

<section class="padding-top-large padding-bottom-large  section-type-column" style="background-color: <?php the_field('section_10_bg_color'); ?>;" id="section-investment-philosophy-and-portfolios">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	<h2 style="text-align: center;"><?php the_field('section_10_title'); ?></h2>
            
                <div class="nt-nt_accordions-wrap" data-active="0">
                
                    <?php if(get_field('section_10_content')): while(has_sub_field('section_10_content')): ?>
                    <div class="tab">
                    
                        <i class="nt-icon-plus"></i><i class="nt-icon-minus"></i> <?php the_sub_field('section_10_sub_title'); ?>
                    
                    </div>
                
                    <div class="pane clearfix">
                    
                    	<?php the_sub_field('section_10_sub_content'); ?>
                        
                    
                    </div>
                    <?php endwhile; endif; ?>
                
                </div>
            	
                <h5><a href="#section-topics" class="button">Back to Top</a></h5>
            
            </div>
        
        </div>
    
    </div>

</section>

<section class="padding-top-large padding-bottom-large  section-type-column" style="background-color: <?php the_field('section_11_bg_color'); ?>;" id="section-integration">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	<h2 style="text-align: center;"><?php the_field('section_11_title'); ?></h2>
            
                <div class="nt-nt_accordions-wrap" data-active="0">
                
                    <?php if(get_field('section_11_content')): while(has_sub_field('section_11_content')): ?>
                    <div class="tab">
                    
                        <i class="nt-icon-plus"></i><i class="nt-icon-minus"></i> <?php the_sub_field('section_11_sub_title'); ?>
                    
                    </div>
                
                    <div class="pane clearfix">
                    
                    	<?php the_sub_field('section_11_sub_content'); ?>
                        
                    
                    </div>
                    <?php endwhile; endif; ?>
                
                </div>
            	
                <h5><a href="#section-topics" class="button">Back to Top</a></h5>
            
            </div>
        
        </div>
    
    </div>

</section>

<section class="padding-top-large padding-bottom-large  section-type-column" style="background-color:<?php the_field('section_12_bg_color'); ?>;" id="section-compliance">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	<h2 style="text-align: center;"><?php the_field('section_12_title'); ?></h2>
            
                <div class="nt-nt_accordions-wrap" data-active="1">
                
                    <?php if(get_field('section_12_content')): while(has_sub_field('section_12_content')): ?>
                    <div class="tab">
                    
                        <i class="nt-icon-plus"></i><i class="nt-icon-minus"></i> <?php the_sub_field('section_12_sub_title'); ?>
                    
                    </div>
                
                    <div class="pane clearfix">
                    
                    	<?php the_sub_field('section_12_sub_content'); ?>
                        
                    
                    </div>
                    <?php endwhile; endif; ?>
                
                </div>
            	
                <h5><a href="#section-topics" class="button">Back to Top</a></h5>
            
            </div>
        
        </div>
    
    </div>

</section>

<section class="padding-top-large padding-bottom-large  section-type-column" style="background-color: <?php the_field('section_13_bg_color'); ?>;" id="section-taxes-and-tax-loss-harvesting">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	<h2 style="text-align: center;"><?php the_field('section_13_title'); ?></h2>
            
                <div class="nt-nt_accordions-wrap" data-active="0">
                
                    <?php if(get_field('section_13_content')): while(has_sub_field('section_13_content')): ?>
                    <div class="tab">
                    
                        <i class="nt-icon-plus"></i><i class="nt-icon-minus"></i> <?php the_sub_field('section_13_sub_title'); ?>
                    
                    </div>
                
                    <div class="pane clearfix">
                    
                    	<?php the_sub_field('section_13_sub_content'); ?>
                        
                    
                    </div>
                    <?php endwhile; endif; ?>
                
                </div>
            	
                <h5><a href="#section-topics" class="button">Back to Top</a></h5>
            
            </div>
        
        </div>
    
    </div>

</section>

<section class="padding-top-large padding-bottom-large  section-type-column" style="background-color: <?php the_field('section_14_bg_color'); ?>;" id="section-iras-and-rollovers">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	<h2 style="text-align: center;"><?php the_field('section_14_title'); ?></h2>
            
                <div class="nt-nt_accordions-wrap" data-active="0">
                
                    <?php if(get_field('section_14_content')): while(has_sub_field('section_14_content')): ?>
                    <div class="tab">
                    
                        <i class="nt-icon-plus"></i><i class="nt-icon-minus"></i> <?php the_sub_field('section_14_sub_title'); ?>
                    
                    </div>
                
                    <div class="pane clearfix">
                    
                    	<?php the_sub_field('section_14_sub_content'); ?>
                        
                    
                    </div>
                    <?php endwhile; endif; ?>
                
                </div>
            	
                <h5><a href="#section-topics" class="button">Back to Top</a></h5>
            
            </div>
        
        </div>
    
    </div>

</section>

<section class="padding-top-large padding-bottom-large  section-type-column" style="background-color: <?php the_field('section_15_bg_color'); ?>;" id="section-trust-accounts">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	<h2 style="text-align: center;"><?php the_field('section_15_title'); ?></h2>
            
                <div class="nt-nt_accordions-wrap" data-active="0">
                
                    <?php if(get_field('section_15_content')): while(has_sub_field('section_15_content')): ?>
                    <div class="tab">
                    
                        <i class="nt-icon-plus"></i><i class="nt-icon-minus"></i> <?php the_sub_field('section_15_sub_title'); ?>
                    
                    </div>
                
                    <div class="pane clearfix">
                    
                    	<?php the_sub_field('section_15_sub_content'); ?>
                        
                    
                    </div>
                    <?php endwhile; endif; ?>
                
                </div>
            	
                <h5><a href="#section-topics" class="button">Back to Top</a></h5>
            
            </div>
        
        </div>
    
    </div>

</section>



<section class="padding-top-large padding-bottom-large  section-type-column" style="background-color: <?php the_field('section_16_bg_color'); ?>;" id="section-joint-accounts">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	<h2 style="text-align: center;"><?php the_field('section_16_title'); ?></h2>
            
                <div class="nt-nt_accordions-wrap" data-active="0">
                
                    <?php if(get_field('section_16_content')): while(has_sub_field('section_16_content')): ?>
                    <div class="tab">
                    
                        <i class="nt-icon-plus"></i><i class="nt-icon-minus"></i> <?php the_sub_field('section_16_sub_title'); ?>
                    
                    </div>
                
                    <div class="pane clearfix">
                    
                    	<?php the_sub_field('section_16_sub_content'); ?>
                        
                    
                    </div>
                    <?php endwhile; endif; ?>
                
                </div>
            	
                <h5><a href="#section-topics" class="button">Back to Top</a></h5>
            
            </div>
        
        </div>
    
    </div>

</section>



<section class="padding-top-large padding-bottom-large  section-type-column" style="background-color: <?php the_field('section_17_bg_color'); ?>;" id="section-returns">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            
            	<h2 style="text-align: center;"><?php the_field('section_17_title'); ?></h2>
            
                <div class="nt-nt_accordions-wrap" data-active="0">
                
                    <?php if(get_field('section_17_content')): while(has_sub_field('section_17_content')): ?>
                    <div class="tab">
                    
                        <i class="nt-icon-plus"></i><i class="nt-icon-minus"></i> <?php the_sub_field('section_17_sub_title'); ?>
                    
                    </div>
                
                    <div class="pane clearfix">
                    
                    	<?php the_sub_field('section_17_sub_content'); ?>
                        
                    
                    </div>
                    <?php endwhile; endif; ?>
                
                </div>
            	
                <h5><a href="#section-topics" class="button">Back to Top</a></h5>
            
            </div>
        
        </div>
    
    </div>

</section>





</div>



<?php endwhile; endif; ?>

<?php get_footer(); ?>
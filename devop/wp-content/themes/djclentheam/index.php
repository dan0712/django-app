<?php get_header(); ?>



<div id="news" class="pagebuilder-content">


<section class="padding-top-large padding-bottom-large  bg-image-cover section-type-intro" id="section-2" style="background-color: #e2e2e2;background-image: url('<?php the_field('section_1_bg', 'option'); ?>');">

	
	
	
</section>

<section class="padding-top-none padding-bottom-none text-color-light section-type-column" style="background-color:<?php the_field('section_2_bg_color', 'option'); ?>;" id="section-4">

    <div class="container">
    
        <div class="row">
        
            <div class="twelve columns col">
            

                <?php the_field('section_2_content', 'option'); ?>

            </div>
        
        </div>
    
    </div>

</section>


<section class="padding-top-large padding-bottom-large bg-image-cover section-type-blog" id="section-1" style="background-color:<?php the_field('section_3_bg_color', 'option'); ?>; ">
	
	
	<div class="row">

        <div class="eight col">
                        
	
            <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
            <div class="grid-mb">
            
                <div id="post-<?php the_ID(); ?>" <?php post_class('blog-post post post-single'); ?>>
                    
                    <div class="post-media">
                        
                    </div>
                
                    <div class="post-bg">
                    
                        <div class="post-title">
                        
                            <h1 class="h3">
                                <a href="<?php echo get_permalink(); ?>"><?php the_title(); ?></a>
                            </h1>
                            
                            <div class="post-meta">
                            
                                By <a href="<?php echo get_permalink(); ?><?php //echo get_author_posts_url( get_the_author_meta( 'ID' ) ); ?>" title="Posts by <?php the_author_meta( 'display_name' ); ?>" rel="author"><?php the_author_meta( 'display_name' ); ?></a>
                                on <a href="<?php echo get_permalink(); ?>">November 26, 2014</a> in  <?php the_category(', '); ?> 
                            
                            </div>
                        
                        </div>
                        
                        <div class="post-body pe-wp-default">
                        
                            <?php the_content(); ?>
                        
                        </div>
                    
                    </div>
                
                </div>
            
            </div>
            <?php endwhile; ?>
            
            <div class="clear"></div>
	
            <div class="pagination">
            <?php if(function_exists('wp_pagenavi')) { wp_pagenavi(); } endif; wp_reset_postdata(); ?>
            </div>
    
    		<div class="clear"></div>
        
        </div>


        <div class="four col">
            <div class="sidebar">
                <?php if ( !function_exists('dynamic_sidebar')|| !dynamic_sidebar('main_sidebar') ) : endif; ?>
            </div>
        </div>
	
    
    
    </div>

</section>

</div>


<?php get_footer(); ?>
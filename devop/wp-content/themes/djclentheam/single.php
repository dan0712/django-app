<?php get_header(); ?>

<div class="blog">
	<div class="row">
		<div class="eight col">




<div class="pe-container pe-block">
					
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
            <?php endwhile; endif; ?>	
		
<!--comment section-->
<div id="comments" class="row-fluid grid-mb">
	<div class="span12 commentsWrap">
		<div class="inner-spacer-right-lrg">

			<div class="row-fluid comments-title-bg">
				<div class="span12">

					<h3 id="comments-title">
						Leave A Comment
					</h3>

				</div>
			</div>

			<div class="commentform-bg">
					
				<div id="respond">

	

	
	<!--comment form-->
	<div class="row-fluid">
		<div class="span12">
			<?php comments_template(); ?> 
		</div>
	</div>
	<!--end comment form-->
	
</div>
<!--end respond--> 

			</div>

		</div>			
	</div>
</div>
<!--end comments-->


	

</div>
		</div>
        
        
        <div class="four col">
            <div class="sidebar">
                <?php if ( !function_exists('dynamic_sidebar')|| !dynamic_sidebar('main_sidebar') ) : endif; ?>
            </div>
        </div>
	
 
    </div>

</div>

<?php get_footer(); ?>
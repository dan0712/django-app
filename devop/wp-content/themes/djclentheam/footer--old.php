	<!-- Back to top -->
	<div class="back-top-wrap">
		<a href="#top" class="scrollto"><i class="back-top fa fa-chevron-up"></i></a>
	</div>




	<!-- Social footer -->
<footer class="footer">
	<div class="row">
		<div class="twelve col">
                    <div class="sf-icons">

                        <?php if(get_field('social_networks', 'option')): while(has_sub_field('social_networks', 'option')): ?>
                			<a href="<?php the_sub_field('social_link'); ?>" target="_blank"><i class="fa fa-<?php the_sub_field('social_network'); ?>"></i></a>
						<?php endwhile; endif; ?>
                        
                    </div>
                    
                    <?php the_field('theme_footer_text', 'option'); ?>
                   
        			
		</div>
	</div>
</footer>
<?php $theme_google_analytics = get_field('theme_google_analytics', 'option'); ?>
<?php if($theme_google_analytics  != ""){ ?>
	<?php echo $theme_google_analytics; ?>
<?php } ?>
<?php wp_footer(); ?>

</body>
</html>
<?php get_header(); ?>

<?php if (have_posts()) : while (have_posts()) : the_post(); ?>



<section id="terms-and-conditions" class="regularpage">
	<div class="row">
		<div class="twelve columns">

			<!-- The title -->
			<div class="title">
				<h1><?php the_title(); ?></h1>
				<hr>
			</div>
			
			<div class="page-body pe-wp-default">
				<?php the_content(); ?>
			</div>

		</div>
	</div>
</section>



<?php endwhile; endif; ?>

<?php get_footer(); ?>
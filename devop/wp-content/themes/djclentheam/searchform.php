<?php
/**
 * default search form
 */
?>

<form class="clearfix" action="<?php echo esc_url( home_url( '/' ) ); ?>">
	<input type="text" value="<?php echo esc_attr( get_search_query() ); ?>" placeholder="Search.." class="search form-control" id="s" name="s">
	<input type="submit" value="Go" class="search-submit btn btn-primary btn-sm margin-top-10">
</form>
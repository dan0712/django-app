# This dockerfile is pulled directly from
# https://github.com/docker-library/wordpress/raw/618490d4bdff6c5774b84b717979bfe3d6ba8ad1/apache/Dockerfile
# It is needed as on bluemix we need the mounted volume below where the data is stored (ie at /var/www) so we can change
# the permissions on the directories, but the std wordpress image mounts a volume at /var/www/html, which splats the
# bluemix mount.

FROM php:5.6-apache

RUN a2enmod rewrite

# install the PHP extensions we need
RUN apt-get update && apt-get install -y libpng12-dev libjpeg-dev vim less && rm -rf /var/lib/apt/lists/* \
	&& docker-php-ext-configure gd --with-png-dir=/usr --with-jpeg-dir=/usr \
	&& docker-php-ext-install gd
RUN docker-php-ext-install mysqli

# Disable this volume as it causes me grief on Bluemix.
# VOLUME /var/www/html

ENV WORDPRESS_VERSION 4.2.1
ENV WORDPRESS_UPSTREAM_VERSION 4.2.1
ENV WORDPRESS_SHA1 c93a39be9911591b19a94743014be3585df0512f

# upstream tarballs include ./wordpress/ so this gives us /usr/src/wordpress
RUN curl -o wordpress.tar.gz -SL https://wordpress.org/wordpress-${WORDPRESS_UPSTREAM_VERSION}.tar.gz \
	&& echo "$WORDPRESS_SHA1 *wordpress.tar.gz" | sha1sum -c - \
	&& tar -xzf wordpress.tar.gz -C /usr/src/ \
	&& rm wordpress.tar.gz \
	&& chown -R www-data:www-data /usr/src/wordpress

COPY docker-entrypoint.sh /entrypoint.sh

# grr, ENTRYPOINT resets CMD now
ENTRYPOINT ["/entrypoint.sh"]
CMD ["apache2-foreground"]
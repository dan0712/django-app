from anymail.signals import tracking
from django.dispatch import receiver
import logging

logger = logging.getLogger('main.email_receivers')


@receiver(tracking)
def handle_delivered(sender, event, esp_name, **kwargs):
    if event.event_type == 'delivered':
        logger.info('Email to recipient %s delivered' % event.recipient)


@receiver(tracking)
def handle_dropped(sender, event, esp_name, **kwargs):
    if event.event_type == 'rejected' or \
       event.event_type == 'bounced' or \
       event.event_type == 'failed':
        logger.error("Email to recipient %s did not make it because of %s" % (event.recipient, event.event_type))

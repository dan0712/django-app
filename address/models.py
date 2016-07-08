from django.db import models

"""
After looking through the addressing options available (django-postal, django-address) Neither worked well with
addresses that have a apartment number, and chinese addresses, and had a DRF backend, so I had to roll my own :(
"""


class Region(models.Model):
    """
    A model of the first-level administrative regions in countries. Examples can be states, cantons, even towns for
    small countries.
    """
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=16, db_index=True, null=True, blank=True)
    country = models.CharField(max_length=2)

    class Meta:
        unique_together = (
            ('country', 'name'),
            ('country', 'code')
        )


class Address(models.Model):
    """
    Because the whole world does addressing wildly differently, the only thing generally in common is country,
    top-level region and some postal code identifier. As such, the best way to do addressing for our
    purpose (which is to send mail and identify) is to simply keep the address lines as a resident would write them.
    This works for PO boxes, houses and lots of other things.
    """
    # An address is always somewhere within a region. Hence one line of addressing is required.
    address = models.TextField(help_text='The full address excluding country, first level administrative region '
                                         '(state/province etc) and postcode')
    post_code = models.CharField(max_length=16, blank=True, null=True)  # Some countries don't have post codes.
    global_id = models.CharField(max_length=64,
                                 blank=True,  # Doesn't really matter, as since it's unique, blank is a valid value.
                                 null=True,
                                 unique=True,
                                 help_text='Global identifier of the address in whatever API we are using (if any)')
    region = models.ForeignKey(Region, related_name='+')

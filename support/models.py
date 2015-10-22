__author__ = 'cristian'
from django.db import models
from tinymce_4.fields import TinyMCEModelField


class SupportPage(models.Model):
    title = models.CharField(max_length=255)
    header_text = TinyMCEModelField(null=True, blank=True)
    body_text = TinyMCEModelField(null=True, blank=True)
    header_background_image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.title

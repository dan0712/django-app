# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce_4.fields


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supportpage',
            name='body_text',
            field=tinymce_4.fields.TinyMCEModelField(null=True),
        ),
        migrations.AlterField(
            model_name='supportpage',
            name='header_background_image',
            field=models.ImageField(null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='supportpage',
            name='header_text',
            field=tinymce_4.fields.TinyMCEModelField(null=True),
        ),
    ]

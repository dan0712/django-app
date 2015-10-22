# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce_4.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SupportPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('header_text', tinymce_4.fields.TinyMCEModelField()),
                ('body_text', tinymce_4.fields.TinyMCEModelField()),
                ('header_background_image', models.ImageField(upload_to='')),
            ],
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_auto_20160406_0419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetclass',
            name='display_name',
            field=models.CharField(unique=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='assetclass',
            name='name',
            field=models.CharField(validators=[django.core.validators.RegexValidator(message='Invalid character only accept (0-9a-zA-Z_) ', regex='^[0-9a-zA-Z_]+$')], unique=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='assetfeaturevalue',
            name='feature',
            field=models.ForeignKey(related_name='values', help_text='The asset feature this is one value for.', to='main.AssetFeature', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='assetfeaturevalue',
            name='name',
            field=models.CharField(help_text='This should be an adjective.', max_length=127),
        ),
        migrations.AlterField(
            model_name='goalmetric',
            name='feature',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.AssetFeatureValue', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='assetfeaturevalue',
            unique_together=set([('name', 'feature')]),
        ),
    ]

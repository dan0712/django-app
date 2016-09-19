# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0057_investmentcycleprediction_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticker',
            name='state',
            field=models.IntegerField(choices=[(1, 'Inactive'), (2, 'Active'), (3, 'Closed')], default=2, help_text='The current state of this ticker.'),
        ),
    ]

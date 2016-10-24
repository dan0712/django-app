# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0057_investmentcycleprediction_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goalmetric',
            name='measured_val',
        ),
    ]

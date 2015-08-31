# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20150828_0225'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('client_email', models.EmailField(max_length=254, unique=True)),
                ('sent_date', models.DateTimeField()),
            ],
        ),
        migrations.AlterField(
            model_name='advisor',
            name='confirmation_key',
            field=models.CharField(max_length=36, null=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='assetclass',
            name='super_asset_class',
            field=models.CharField(max_length=255, choices=[('EQUITY_AU', 'EQUITY_AU'), ('EQUITY_US', 'EQUITY_US'), ('EQUITY_EU', 'EQUITY_EU'), ('EQUITY_EM', 'EQUITY_EM'), ('EQUITY_INT', 'EQUITY_INT'), ('FIXED_INCOME_AU', 'FIXED_INCOME_AU'), ('FIXED_INCOME_US', 'FIXED_INCOME_US'), ('FIXED_INCOME_EU', 'FIXED_INCOME_EU'), ('FIXED_INCOME_EM', 'FIXED_INCOME_EM'), ('FIXED_INCOME_INT', 'FIXED_INCOME_INT')]),
        ),
        migrations.AlterField(
            model_name='firm',
            name='firm_client_agreement_url',
            field=models.FileField(upload_to='', null=True, verbose_name='Client Agreement (PDF)', blank=True),
        ),
        migrations.AlterField(
            model_name='firm',
            name='firm_form_adv_part2_url',
            field=models.FileField(upload_to='', null=True, verbose_name='Form Adv', blank=True),
        ),
        migrations.AlterField(
            model_name='firm',
            name='firm_knocked_out_logo_url',
            field=models.ImageField(upload_to='', verbose_name='Colored logo'),
        ),
        migrations.AlterField(
            model_name='firm',
            name='firm_logo_url',
            field=models.ImageField(upload_to='', verbose_name='White logo'),
        ),
        migrations.AddField(
            model_name='clientinvite',
            name='advisor',
            field=models.ForeignKey(related_name='client_invites', to='main.Advisor'),
        ),
    ]

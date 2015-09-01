# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20150901_1837'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='firmdata',
            options={'verbose_name': 'Firm detail'},
        ),
        migrations.AlterField(
            model_name='firmdata',
            name='afsl_asic',
            field=models.CharField(verbose_name='AFSL/ASIC number', max_length=50),
        ),
        migrations.AlterField(
            model_name='firmdata',
            name='afsl_asic_document',
            field=models.FileField(verbose_name='AFSL/ASIC doc.', upload_to=''),
        ),
        migrations.AlterField(
            model_name='firmdata',
            name='alternate_email_address',
            field=models.EmailField(verbose_name='Email address', max_length=254, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='firmdata',
            name='australian_business_number',
            field=models.CharField(verbose_name='ABN', max_length=20),
        ),
        migrations.AlterField(
            model_name='firmdata',
            name='fee_bank_account_branch_name',
            field=models.CharField(verbose_name='Branch name', max_length=100),
        ),
        migrations.AlterField(
            model_name='firmdata',
            name='fee_bank_account_bsb_number',
            field=models.CharField(verbose_name='BSB number', max_length=20),
        ),
        migrations.AlterField(
            model_name='firmdata',
            name='fee_bank_account_holder_name',
            field=models.CharField(verbose_name='Account holder', max_length=100),
        ),
        migrations.AlterField(
            model_name='firmdata',
            name='fee_bank_account_name',
            field=models.CharField(verbose_name='Name', max_length=100),
        ),
        migrations.AlterField(
            model_name='firmdata',
            name='fee_bank_account_number',
            field=models.CharField(verbose_name='Account number', max_length=20),
        ),
        migrations.AlterField(
            model_name='firmdata',
            name='office_address_line_1',
            field=models.CharField(verbose_name='Office address 1', max_length=255),
        ),
        migrations.AlterField(
            model_name='firmdata',
            name='office_address_line_2',
            field=models.CharField(verbose_name='Office address 2', max_length=255, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='firmdata',
            name='postal_address_line_1',
            field=models.CharField(verbose_name='Postal address 1', max_length=255),
        ),
        migrations.AlterField(
            model_name='firmdata',
            name='postal_address_line_2',
            field=models.CharField(verbose_name='Postal address 2', max_length=255, blank=True, null=True),
        ),
    ]

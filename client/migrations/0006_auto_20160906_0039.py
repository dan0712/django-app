# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0005_clientaccount_account_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='IBAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('ib_account', models.CharField(max_length=32)),
            ],
        ),
        migrations.RemoveField(
            model_name='clientaccount',
            name='account_id',
        ),
        migrations.RemoveField(
            model_name='riskprofileanswer',
            name='score',
        ),
        migrations.AddField(
            model_name='riskprofileanswer',
            name='a_score',
            field=models.FloatField(default=0, help_text='Indication of Ability to take risk. Higher means losses due to risk has less critical impact on the investor'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='riskprofileanswer',
            name='b_score',
            field=models.FloatField(default=0, help_text='Indication of Behaviour towards risk. Higher means higher risk is idealogically acceptable.'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='riskprofileanswer',
            name='image',
            field=models.ImageField(verbose_name='answer_image', upload_to='', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='riskprofileanswer',
            name='s_score',
            field=models.FloatField(default=0, help_text='Indication of Investor sophistication. Higher means investor understands risk and investment matters.'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='riskprofilequestion',
            name='explanation',
            field=models.TextField(default='We do this because we love askig annoying questions'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='riskprofilequestion',
            name='image',
            field=models.ImageField(verbose_name='question_image', upload_to='', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='ibaccount',
            name='bs_account',
            field=models.OneToOneField(related_name='ib_account', to='client.ClientAccount'),
        ),
    ]

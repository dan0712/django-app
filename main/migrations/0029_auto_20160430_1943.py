# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def def_rpg(apps, schema_editor):
    ClientAccount = apps.get_model("main", "ClientAccount")
    RiskProfileGroup = apps.get_model("main", "RiskProfileGroup")
    db_alias = schema_editor.connection.alias

    # First create the default risk profile groups for natural and corporate entities.
    def_nat = RiskProfileGroup.objects.create(name='default_natural',
                                              description='The default risk profile questions for accounts '
                                                          'for natural entities (PERSONAL and JOINT accounts)')
    def_corp = RiskProfileGroup.objects.create(name='default_corporate',
                                               description='The default risk profile questions for accounts '
                                                           'for corporate entities (TRUST, SMSF and CORPORATE)')

    for account in ClientAccount.objects.using(db_alias).all():
        account.risk_profile_group = def_nat if account.account_type < 2 else def_corp
        account.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_auto_20160414_0108'),
    ]

    operations = [
        migrations.CreateModel(
            name='RiskProfileAnswer',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('order', models.IntegerField()),
                ('text', models.TextField()),
                ('score', models.FloatField()),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='RiskProfileGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='RiskProfileQuestion',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('order', models.IntegerField()),
                ('text', models.TextField()),
                ('group', models.ForeignKey(to='main.RiskProfileGroup', related_name='questions')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='riskprofileanswer',
            name='question',
            field=models.ForeignKey(to='main.RiskProfileQuestion', related_name='answers'),
        ),
        migrations.AddField(
            model_name='clientaccount',
            name='risk_profile_group',
            field=models.ForeignKey(null=True, related_name='accounts', to='main.RiskProfileGroup'),
        ),
        migrations.AlterUniqueTogether(
            name='riskprofilequestion',
            unique_together=set([('group', 'order')]),
        ),
        migrations.AlterUniqueTogether(
            name='riskprofileanswer',
            unique_together=set([('question', 'order')]),
        ),
        migrations.RunPython(def_rpg),
        migrations.AlterField(
            model_name='clientaccount',
            name='risk_profile_group',
            field=models.ForeignKey(related_name='accounts', to='main.RiskProfileGroup'),
        ),
        migrations.AddField(
            model_name='clientaccount',
            name='risk_profile_responses',
            field=models.ManyToManyField(to='main.RiskProfileAnswer'),
        ),
    ]

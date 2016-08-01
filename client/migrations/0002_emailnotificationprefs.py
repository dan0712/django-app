# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def create_for_clients(apps, schema_editor):
    Client = apps.get_model("client", "Client")
    EmailNotificationPrefs = apps.get_model("client", "EmailNotificationPrefs")
    db_alias = schema_editor.connection.alias
    EmailNotificationPrefs.objects.using(db_alias).bulk_create([
        EmailNotificationPrefs(client=client)
        for client in Client.objects.all()
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailNotificationPrefs',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('auto_deposit', models.BooleanField(verbose_name='to remind me a day before my automatic deposits will be transferred', default=True)),
                ('hit_10mln', models.BooleanField(verbose_name='when my account balance hits $10,000,000', default=False)),
                ('client', models.OneToOneField(related_name='notification_prefs', to='client.Client')),
            ],
        ),
        migrations.RunPython(create_for_clients, lambda *x:True)
    ]

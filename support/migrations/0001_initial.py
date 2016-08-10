# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import migrations, models

from common.constants import GROUP_SUPPORT_STAFF

def create_group(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Group.objects.using(db_alias).create(name=GROUP_SUPPORT_STAFF)


def delete_group(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Group.objects.using(db_alias).filter(name=GROUP_SUPPORT_STAFF).delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('ticket', models.CharField(unique=True, max_length=30)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('staff', models.ForeignKey(related_name='gave_support', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='had_support', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('can_create_support_requests', 'Can create support requests'),),
            },
        ),
        migrations.RunPython(create_group, delete_group),
    ]

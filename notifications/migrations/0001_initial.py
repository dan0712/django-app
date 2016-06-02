# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import jsonfield.fields
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('level', models.CharField(default='info', choices=[('success', 'success'), ('info', 'info'), ('warning', 'warning'), ('error', 'error')], max_length=20)),
                ('unread', models.BooleanField(default=True)),
                ('actor_object_id', models.PositiveIntegerField()),
                ('verb', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('target_object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('action_object_object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('public', models.BooleanField(default=True)),
                ('deleted', models.BooleanField(default=False)),
                ('emailed', models.BooleanField(default=False)),
                ('data', jsonfield.fields.JSONField(blank=True, null=True)),
                ('action_object_content_type', models.ForeignKey(null=True, blank=True, related_name='notify_action_object', to='contenttypes.ContentType')),
                ('actor_content_type', models.ForeignKey(to='contenttypes.ContentType', related_name='notify_actor')),
                ('recipient', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='notifications')),
                ('target_content_type', models.ForeignKey(null=True, blank=True, related_name='notify_target', to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('-timestamp',),
            },
        ),
    ]

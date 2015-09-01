# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailInvitation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('object_id', models.PositiveIntegerField()),
                ('send_date', models.DateTimeField(auto_now=True)),
                ('send_count', models.PositiveIntegerField(default=0)),
                ('status', models.PositiveIntegerField(default=0, choices=[(0, 'Pending'), (1, 'Submitted'), (3, 'Active'), (4, 'Closed')])),
                ('invitation_type', models.PositiveIntegerField(default=3, choices=[(0, 'Advisor'), (1, 'Legal representative'), (3, 'Client'), (2, 'Supervisor')])),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.RemoveField(
            model_name='clientinvite',
            name='advisor',
        ),
        migrations.DeleteModel(
            name='ClientInvite',
        ),
    ]

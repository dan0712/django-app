# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict

from django.db import migrations


def rename_dups(apps, schema_editor):
    Goal = apps.get_model("main", "Goal")
    db_alias = schema_editor.connection.alias
    names = defaultdict(int)
    for goal in Goal.objects.using(db_alias).all():
        if goal.state == 3:
            goal.name += '_ARCHIVED'
        nid = (goal.account_id, goal.name)
        if nid in names:
            goal.name += '_{}'.format(names[nid] + 1)
        names[nid] += 1
        goal.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_auto_20160406_0045'),
    ]

    operations = [
        migrations.RunPython(rename_dups),
        migrations.AlterUniqueTogether(
            name='goal',
            unique_together=set([('account', 'name')]),
        ),
    ]

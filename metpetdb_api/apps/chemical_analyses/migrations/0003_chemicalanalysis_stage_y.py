# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chemical_analyses', '0002_auto_20150907_2005'),
    ]

    operations = [
        migrations.AddField(
            model_name='chemicalanalysis',
            name='stage_y',
            field=models.FloatField(blank=True, null=True),
        ),
    ]

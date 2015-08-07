# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SampleMapping',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, editable=False)),
                ('old_sample_id', models.IntegerField()),
                ('new_sample_id', models.UUIDField()),
            ],
            options={
                'db_table': 'sample_mapping',
            },
        ),
    ]

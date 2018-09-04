# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-08-26 16:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0010_auto_20180619_0455'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='description',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='scale',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
    ]

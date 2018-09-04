# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-08-27 02:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0012_remove_image_chemical_analysis'),
        ('chemical_analyses', '0004_auto_20180220_0409'),
    ]

    operations = [
        migrations.AddField(
            model_name='chemicalanalysis',
            name='reference_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='chemical_analyses', to='images.Image'),
        ),
    ]
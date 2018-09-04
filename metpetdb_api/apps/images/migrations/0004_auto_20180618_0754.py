# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-06-18 07:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0003_auto_20180618_0655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='chemical_analysis',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='chemical_analyses.ChemicalAnalysis'),
        ),
        migrations.AlterField(
            model_name='image',
            name='sample',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='samples.Sample'),
        ),
        migrations.AlterField(
            model_name='image',
            name='subsample',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='samples.Subsample'),
        ),
    ]

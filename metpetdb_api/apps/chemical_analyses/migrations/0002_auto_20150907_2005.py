# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chemical_analyses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chemicalanalysis',
            name='mineral',
            field=models.ForeignKey(null=True, to='samples.Mineral', blank=True),
        ),
        migrations.AddField(
            model_name='chemicalanalysis',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='chemical_analyses'),
        ),
        migrations.AddField(
            model_name='chemicalanalysis',
            name='oxides',
            field=models.ManyToManyField(through='chemical_analyses.ChemicalAnalysisOxide', to='chemical_analyses.Oxide'),
        ),
        migrations.AddField(
            model_name='chemicalanalysis',
            name='subsample',
            field=models.ForeignKey(to='samples.Subsample', related_name='chemical_analyses'),
        ),
        migrations.AlterUniqueTogether(
            name='chemicalanalysisoxide',
            unique_together=set([('chemical_analysis', 'oxide')]),
        ),
    ]

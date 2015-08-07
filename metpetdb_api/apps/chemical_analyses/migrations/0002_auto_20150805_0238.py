# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('chemical_analyses', '0001_initial'),
        ('samples', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='chemicalanalyses',
            name='mineral',
            field=models.ForeignKey(blank=True, null=True, to='samples.Mineral'),
        ),
        migrations.AddField(
            model_name='chemicalanalyses',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='chemical_analyses'),
        ),
        migrations.AddField(
            model_name='chemicalanalyses',
            name='oxides',
            field=models.ManyToManyField(through='chemical_analyses.ChemicalAnalysisOxide', to='chemical_analyses.Oxide'),
        ),
        migrations.AddField(
            model_name='chemicalanalyses',
            name='subsample',
            field=models.ForeignKey(to='samples.Subsample'),
        ),
        migrations.AlterUniqueTogether(
            name='chemicalanalysisoxide',
            unique_together=set([('chemical_analysis', 'oxide')]),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
import concurrency.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChemicalAnalysis',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('version', concurrency.fields.AutoIncVersionField(help_text='record revision number', default=0)),
                ('public_data', models.BooleanField(default=False)),
                ('reference_x', models.FloatField(blank=True, null=True)),
                ('reference_y', models.FloatField(blank=True, null=True)),
                ('stage_x', models.FloatField(blank=True, null=True)),
                ('analysis_method', models.CharField(blank=True, max_length=50, null=True)),
                ('where_done', models.CharField(blank=True, max_length=50, null=True)),
                ('analyst', models.CharField(blank=True, max_length=50, null=True)),
                ('analysis_date', models.DateTimeField(blank=True, null=True)),
                ('date_precision', models.SmallIntegerField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=1024, null=True)),
                ('total', models.FloatField(blank=True, null=True)),
                ('spot_id', models.BigIntegerField()),
                ('reference', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'chemical_analyses',
            },
        ),
        migrations.CreateModel(
            name='ChemicalAnalysisElement',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('amount', models.FloatField()),
                ('precision', models.FloatField(blank=True, null=True)),
                ('precision_type', models.CharField(blank=True, max_length=3, null=True)),
                ('measurement_unit', models.CharField(blank=True, max_length=4, null=True)),
                ('min_amount', models.FloatField(blank=True, null=True)),
                ('max_amount', models.FloatField(blank=True, null=True)),
                ('chemical_analysis', models.ForeignKey(to='chemical_analyses.ChemicalAnalysis')),
            ],
            options={
                'db_table': 'chemical_analysis_elements',
            },
        ),
        migrations.CreateModel(
            name='ChemicalAnalysisOxide',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('amount', models.FloatField()),
                ('precision', models.FloatField(blank=True, null=True)),
                ('precision_type', models.CharField(blank=True, max_length=3, null=True)),
                ('measurement_unit', models.CharField(blank=True, max_length=4, null=True)),
                ('min_amount', models.FloatField(blank=True, null=True)),
                ('max_amount', models.FloatField(blank=True, null=True)),
                ('chemical_analysis', models.ForeignKey(to='chemical_analyses.ChemicalAnalysis')),
            ],
            options={
                'db_table': 'chemical_analysis_oxides',
            },
        ),
        migrations.CreateModel(
            name='Element',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('alternate_name', models.CharField(blank=True, max_length=100, null=True)),
                ('symbol', models.CharField(max_length=4, unique=True)),
                ('atomic_number', models.IntegerField()),
                ('weight', models.FloatField(blank=True, null=True)),
                ('order_id', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'elements',
            },
        ),
        migrations.CreateModel(
            name='Oxide',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('oxidation_state', models.SmallIntegerField(blank=True, null=True)),
                ('species', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('weight', models.FloatField(blank=True, null=True)),
                ('cations_per_oxide', models.SmallIntegerField(blank=True, null=True)),
                ('conversion_factor', models.FloatField()),
                ('order_id', models.IntegerField(blank=True, null=True)),
                ('element', models.ForeignKey(to='chemical_analyses.Element')),
            ],
            options={
                'db_table': 'oxides',
            },
        ),
        migrations.AddField(
            model_name='chemicalanalysisoxide',
            name='oxide',
            field=models.ForeignKey(to='chemical_analyses.Oxide'),
        ),
        migrations.AddField(
            model_name='chemicalanalysiselement',
            name='element',
            field=models.ForeignKey(to='chemical_analyses.Element'),
        ),
        migrations.AddField(
            model_name='chemicalanalysis',
            name='elements',
            field=models.ManyToManyField(through='chemical_analyses.ChemicalAnalysisElement', to='chemical_analyses.Element'),
        ),
    ]

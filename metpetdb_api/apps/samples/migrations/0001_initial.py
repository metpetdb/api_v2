# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
import concurrency.fields
import uuid
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Collector',
            fields=[
                ('id', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
            ],
            options={
                'db_table': 'collectors',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'countries',
            },
        ),
        migrations.CreateModel(
            name='Grid',
            fields=[
                ('id', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('version', concurrency.fields.AutoIncVersionField(help_text='record revision number', default=0)),
                ('width', models.SmallIntegerField()),
                ('height', models.SmallIntegerField()),
                ('public_data', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'grids',
            },
        ),
        migrations.CreateModel(
            name='MetamorphicGrade',
            fields=[
                ('id', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'metamorphic_grades',
            },
        ),
        migrations.CreateModel(
            name='MetamorphicRegion',
            fields=[
                ('id', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('shape', django.contrib.gis.db.models.fields.GeometryField(blank=True, srid=4326, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('label_location', django.contrib.gis.db.models.fields.GeometryField(blank=True, srid=4326, null=True)),
            ],
            options={
                'db_table': 'metamorphic_regions',
            },
        ),
        migrations.CreateModel(
            name='Mineral',
            fields=[
                ('id', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'minerals',
            },
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'references',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'regions',
            },
        ),
        migrations.CreateModel(
            name='RockType',
            fields=[
                ('id', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'rock_types',
            },
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('version', concurrency.fields.AutoIncVersionField(help_text='record revision number', default=0)),
                ('public_data', models.BooleanField(default=False)),
                ('number', models.CharField(max_length=35)),
                ('aliases', django.contrib.postgres.fields.ArrayField(blank=True, base_field=models.CharField(blank=True, max_length=35), size=None, null=True)),
                ('collection_date', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('location_name', models.CharField(blank=True, null=True, max_length=50)),
                ('location_coords', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('location_error', models.FloatField(blank=True, null=True)),
                ('date_precision', models.SmallIntegerField(blank=True, null=True)),
                ('country', models.CharField(blank=True, null=True, max_length=100)),
                ('regions', django.contrib.postgres.fields.ArrayField(blank=True, base_field=models.CharField(blank=True, max_length=100), size=None, null=True)),
                ('references', django.contrib.postgres.fields.ArrayField(blank=True, base_field=models.CharField(blank=True, max_length=100), size=None, null=True)),
                ('collector_name', models.CharField(blank=True, null=True, max_length=50)),
                ('sesar_number', models.CharField(blank=True, null=True, max_length=9)),
            ],
            options={
                'db_table': 'samples',
            },
        ),
        migrations.CreateModel(
            name='SampleMineral',
            fields=[
                ('id', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('amount', models.CharField(blank=True, null=True, max_length=30)),
            ],
            options={
                'db_table': 'sample_minerals',
            },
        ),
        migrations.CreateModel(
            name='Subsample',
            fields=[
                ('id', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('version', concurrency.fields.AutoIncVersionField(help_text='record revision number', default=0)),
                ('public_data', models.BooleanField(default=False)),
                ('sample', models.ForeignKey(to='samples.Sample')),
            ],
            options={
                'db_table': 'subsamples',
            },
        ),
        migrations.CreateModel(
            name='SubsampleType',
            fields=[
                ('id', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'subsample_types',
            },
        ),
        migrations.AddField(
            model_name='subsample',
            name='subsample_type',
            field=models.ForeignKey(to='samples.SubsampleType'),
        ),
    ]

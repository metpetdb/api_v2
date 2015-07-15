# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import concurrency.fields
import django.contrib.gis.db.models.fields
import uuid
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Collector',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True, editable=False)),
                ('name', models.CharField(unique=True, max_length=50)),
            ],
            options={
                'db_table': 'collectors',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True, editable=False)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'countries',
            },
        ),
        migrations.CreateModel(
            name='Grid',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True, editable=False)),
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
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True, editable=False)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'metamorphic_grades',
            },
        ),
        migrations.CreateModel(
            name='MetamorphicRegion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True, editable=False)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('shape', django.contrib.gis.db.models.fields.GeometryField(srid=4326, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('label_location', django.contrib.gis.db.models.fields.GeometryField(srid=4326, null=True, blank=True)),
            ],
            options={
                'db_table': 'metamorphic_regions',
            },
        ),
        migrations.CreateModel(
            name='Mineral',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True, editable=False)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'minerals',
            },
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True, editable=False)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'references',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True, editable=False)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'regions',
            },
        ),
        migrations.CreateModel(
            name='RockType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True, editable=False)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'rock_types',
            },
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True, editable=False)),
                ('version', concurrency.fields.AutoIncVersionField(help_text='record revision number', default=0)),
                ('public_data', models.BooleanField(default=False)),
                ('number', models.CharField(max_length=35)),
                ('aliases', django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.CharField(max_length=35, blank=True), blank=True)),
                ('collection_date', models.DateTimeField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('location_name', models.CharField(null=True, max_length=50, blank=True)),
                ('location_coords', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('location_error', models.FloatField(null=True, blank=True)),
                ('date_precision', models.SmallIntegerField(null=True, blank=True)),
                ('country', models.CharField(null=True, max_length=100, blank=True)),
                ('regions', django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.CharField(max_length=100, blank=True), blank=True)),
                ('references', django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.CharField(max_length=100, blank=True), blank=True)),
                ('collector_name', models.CharField(null=True, max_length=50, blank=True)),
                ('sesar_number', models.CharField(null=True, max_length=9, blank=True)),
            ],
            options={
                'db_table': 'samples',
            },
        ),
        migrations.CreateModel(
            name='SampleMineral',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True, editable=False)),
                ('amount', models.CharField(null=True, max_length=30, blank=True)),
            ],
            options={
                'db_table': 'sample_minerals',
            },
        ),
        migrations.CreateModel(
            name='Subsample',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True, editable=False)),
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
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True, editable=False)),
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

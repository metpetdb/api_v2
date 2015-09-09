# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields
import uuid
import django.contrib.gis.db.models.fields
import concurrency.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chemical_analyses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collector',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'db_table': 'collectors',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'db_table': 'countries',
            },
        ),
        migrations.CreateModel(
            name='GeoReference',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('name', models.TextField(unique=True)),
                ('title', models.TextField(blank=True, null=True)),
                ('first_author', models.TextField(blank=True, null=True)),
                ('second_authors', models.TextField(blank=True, null=True)),
                ('journal_name', models.TextField(blank=True, null=True)),
                ('full_text', models.TextField(blank=True, null=True)),
                ('journal_name_2', models.TextField(blank=True, null=True)),
                ('doi', models.TextField(blank=True, null=True)),
                ('publication_year', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'georeferences',
            },
        ),
        migrations.CreateModel(
            name='Grid',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
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
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'db_table': 'metamorphic_grades',
            },
        ),
        migrations.CreateModel(
            name='MetamorphicRegion',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('shape', django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=4326)),
                ('description', models.TextField(blank=True, null=True)),
                ('label_location', django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=4326)),
            ],
            options={
                'db_table': 'metamorphic_regions',
            },
        ),
        migrations.CreateModel(
            name='Mineral',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('real_mineral', models.ForeignKey(null=True, to='samples.Mineral', blank=True)),
            ],
            options={
                'db_table': 'minerals',
            },
        ),
        migrations.CreateModel(
            name='MineralRelationship',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('child_mineral', models.ForeignKey(to='samples.Mineral', related_name='child')),
                ('parent_mineral', models.ForeignKey(to='samples.Mineral', related_name='parent')),
            ],
            options={
                'db_table': 'mineral_relationships',
            },
        ),
        migrations.CreateModel(
            name='MineralType',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('name', models.CharField(max_length=50)),
                ('elements', models.ManyToManyField(to='chemical_analyses.Element', related_name='mineral_types')),
                ('oxides', models.ManyToManyField(to='chemical_analyses.Oxide', related_name='mineral_types')),
            ],
            options={
                'db_table': 'mineral_types',
            },
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'db_table': 'references',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'db_table': 'regions',
            },
        ),
        migrations.CreateModel(
            name='RockType',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'db_table': 'rock_types',
            },
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('version', concurrency.fields.AutoIncVersionField(help_text='record revision number', default=0)),
                ('public_data', models.BooleanField(default=False)),
                ('number', models.CharField(max_length=35)),
                ('aliases', django.contrib.postgres.fields.ArrayField(blank=True, base_field=models.CharField(blank=True, max_length=35), null=True, size=None)),
                ('collection_date', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('location_name', models.CharField(blank=True, max_length=50, null=True)),
                ('location_coords', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('location_error', models.FloatField(blank=True, null=True)),
                ('date_precision', models.SmallIntegerField(blank=True, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('regions', django.contrib.postgres.fields.ArrayField(blank=True, base_field=models.CharField(blank=True, max_length=100), null=True, size=None)),
                ('collector_name', models.CharField(blank=True, max_length=50, null=True)),
                ('sesar_number', models.CharField(blank=True, max_length=9, null=True)),
                ('collector_id', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='+', blank=True, db_column='collector_id')),
                ('metamorphic_grades', models.ManyToManyField(to='samples.MetamorphicGrade')),
                ('metamorphic_regions', models.ManyToManyField(to='samples.MetamorphicRegion')),
            ],
            options={
                'db_table': 'samples',
            },
        ),
        migrations.CreateModel(
            name='SampleMapping',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('old_sample_id', models.IntegerField()),
                ('new_sample_id', models.UUIDField()),
            ],
            options={
                'db_table': 'sample_mapping',
            },
        ),
        migrations.CreateModel(
            name='SampleMineral',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('amount', models.CharField(blank=True, max_length=30, null=True)),
                ('mineral', models.ForeignKey(to='samples.Mineral')),
                ('sample', models.ForeignKey(to='samples.Sample')),
            ],
            options={
                'db_table': 'sample_minerals',
            },
        ),
        migrations.CreateModel(
            name='Subsample',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('name', models.CharField(max_length=100)),
                ('version', concurrency.fields.AutoIncVersionField(help_text='record revision number', default=0)),
                ('public_data', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('sample', models.ForeignKey(to='samples.Sample', related_name='subsamples')),
            ],
            options={
                'db_table': 'subsamples',
            },
        ),
        migrations.CreateModel(
            name='SubsampleType',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('name', models.CharField(max_length=100, unique=True)),
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
        migrations.AddField(
            model_name='sample',
            name='minerals',
            field=models.ManyToManyField(to='samples.Mineral', related_name='samples', through='samples.SampleMineral'),
        ),
        migrations.AddField(
            model_name='sample',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='samples'),
        ),
        migrations.AddField(
            model_name='sample',
            name='references',
            field=models.ManyToManyField(to='samples.GeoReference', related_name='samples'),
        ),
        migrations.AddField(
            model_name='sample',
            name='rock_type',
            field=models.ForeignKey(to='samples.RockType'),
        ),
        migrations.AddField(
            model_name='grid',
            name='subsample',
            field=models.ForeignKey(to='samples.Subsample'),
        ),
        migrations.AlterUniqueTogether(
            name='mineralrelationship',
            unique_together=set([('parent_mineral', 'child_mineral')]),
        ),
    ]

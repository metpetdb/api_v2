# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields
from django.conf import settings
import django.contrib.gis.db.models.fields
import uuid
import concurrency.fields


class Migration(migrations.Migration):

    dependencies = [
        ('chemical_analyses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Collector',
            fields=[
                ('id', models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=50)),
            ],
            options={
                'db_table': 'collectors',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'countries',
            },
        ),
        migrations.CreateModel(
            name='Grid',
            fields=[
                ('id', models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True, serialize=False)),
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
                ('id', models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'metamorphic_grades',
            },
        ),
        migrations.CreateModel(
            name='MetamorphicRegion',
            fields=[
                ('id', models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True, serialize=False)),
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
                ('id', models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('real_mineral', models.ForeignKey(blank=True, null=True, to='samples.Mineral')),
            ],
            options={
                'db_table': 'minerals',
            },
        ),
        migrations.CreateModel(
            name='MineralRelationship',
            fields=[
                ('id', models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True, serialize=False)),
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
                ('id', models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True, serialize=False)),
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
                ('id', models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'references',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'regions',
            },
        ),
        migrations.CreateModel(
            name='RockType',
            fields=[
                ('id', models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'db_table': 'rock_types',
            },
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True, serialize=False)),
                ('version', concurrency.fields.AutoIncVersionField(help_text='record revision number', default=0)),
                ('public_data', models.BooleanField(default=False)),
                ('number', models.CharField(max_length=35)),
                ('aliases', django.contrib.postgres.fields.ArrayField(size=None, blank=True, base_field=models.CharField(blank=True, max_length=35), null=True)),
                ('collection_date', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('location_name', models.CharField(blank=True, max_length=50, null=True)),
                ('location_coords', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('location_error', models.FloatField(blank=True, null=True)),
                ('date_precision', models.SmallIntegerField(blank=True, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('regions', django.contrib.postgres.fields.ArrayField(size=None, blank=True, base_field=models.CharField(blank=True, max_length=100), null=True)),
                ('references', django.contrib.postgres.fields.ArrayField(size=None, blank=True, base_field=models.CharField(blank=True, max_length=100), null=True)),
                ('collector_name', models.CharField(blank=True, max_length=50, null=True)),
                ('sesar_number', models.CharField(blank=True, max_length=9, null=True)),
                ('collector_id', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, db_column='collector_id', related_name='+')),
                ('metamorphic_grades', models.ManyToManyField(to='samples.MetamorphicGrade')),
                ('metamorphic_regions', models.ManyToManyField(to='samples.MetamorphicRegion')),
            ],
            options={
                'db_table': 'samples',
            },
        ),
        migrations.CreateModel(
            name='SampleMineral',
            fields=[
                ('id', models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True, serialize=False)),
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
                ('id', models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('version', concurrency.fields.AutoIncVersionField(help_text='record revision number', default=0)),
                ('public_data', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('sample', models.ForeignKey(to='samples.Sample')),
            ],
            options={
                'db_table': 'subsamples',
            },
        ),
        migrations.CreateModel(
            name='SubsampleType',
            fields=[
                ('id', models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True, serialize=False)),
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
        migrations.AddField(
            model_name='sample',
            name='minerals',
            field=models.ManyToManyField(through='samples.SampleMineral', to='samples.Mineral', related_name='samples'),
        ),
        migrations.AddField(
            model_name='sample',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='samples'),
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

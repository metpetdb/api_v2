import uuid
from concurrency.fields import AutoIncVersionField

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from apps.chemical_analyses.shared_models import Element, Oxide


class BulkUpload(models.Model):
    pass

class RockType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        db_table = 'rock_types'
        ordering = ['name']


class Sample(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = AutoIncVersionField()
    public_data = models.BooleanField(default=False)
    number = models.CharField(max_length=35)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='samples')
    aliases = ArrayField(models.CharField(max_length=35, blank=True),
                         blank=True,
                         null=True)
    collection_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    location_name = models.CharField(max_length=50, blank=True, null=True)
    location_coords = models.PointField()
    location_error = models.FloatField(blank=True, null=True)
    rock_type = models.ForeignKey(RockType)
    date_precision = models.SmallIntegerField(blank=True, null=True)
    metamorphic_regions = models.ManyToManyField('MetamorphicRegion')
    metamorphic_grades = models.ManyToManyField('MetamorphicGrade')
    minerals = models.ManyToManyField('Mineral', through='SampleMineral',
                                      related_name='samples')
    references = models.ManyToManyField('GeoReference', related_name='samples')

    # Free-text field. Ugh. Stored as an CharField to avoid joining to the
    # country table every time we retrieve sample(s).
    country = models.CharField(max_length=100, blank=True, null=True)

    # Free-text field; stored as an ArrayField to avoid joining to the
    # regions table every time we retrieve sample(s).
    regions = ArrayField(models.CharField(max_length=100, blank=True),
                         blank=True,
                         null=True)

    # Free text field with no validation;
    collector_name = models.CharField(max_length=50, blank=True, null=True)

    # Unused; here for backward compatibility
    collector_id = models.ForeignKey(settings.AUTH_USER_MODEL,
                                     db_column='collector_id',
                                     related_name='+',
                                     blank=True,
                                     null=True)

    # Unused; here for backward compatibility
    sesar_number = models.CharField(max_length=9, blank=True, null=True)

    class Meta:
        db_table = 'samples'
        ordering = ['id']


class SubsampleType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        db_table = 'subsample_types'
        ordering = ['id']


class Subsample(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    version = AutoIncVersionField()
    sample = models.ForeignKey(Sample, related_name='subsamples')
    public_data = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='subsamples')
    subsample_type = models.ForeignKey(SubsampleType)

    class Meta:
        db_table = 'subsamples'
        ordering = ['id']


class Grid(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = AutoIncVersionField()
    subsample = models.ForeignKey(Subsample)
    width = models.SmallIntegerField()
    height = models.SmallIntegerField()
    public_data = models.BooleanField(default=False)

    class Meta:
        db_table = 'grids'


class MetamorphicGrade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        db_table = 'metamorphic_grades'
        ordering = ['name']


class MetamorphicRegion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=100)
    shape = models.GeometryField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    label_location = models.GeometryField(blank=True, null=True)

    class Meta:
        db_table = 'metamorphic_regions'
        ordering = ['name']


class Mineral(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=100)
    # real_mineral is supposed to be NOT NULL, but it's not possible to run
    # the migration with that restriction, so here we go; this can be fixed
    # once the app goes into production.
    real_mineral = models.ForeignKey('self',
                                     blank=True,
                                     null=True)

    class Meta:
        db_table = 'minerals'
        ordering = ['name']


class SampleMineral(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sample = models.ForeignKey(Sample)
    mineral = models.ForeignKey(Mineral)
    amount = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        db_table = 'sample_minerals'


class MineralRelationship(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent_mineral = models.ForeignKey(Mineral, related_name='parent')
    child_mineral = models.ForeignKey(Mineral, related_name='child')

    class Meta:
        db_table = 'mineral_relationships'
        unique_together = (('parent_mineral', 'child_mineral'),)


class MineralType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)

    elements = models.ManyToManyField(Element,
                                      related_name='mineral_types')
    oxides = models.ManyToManyField(Oxide,
                                    related_name='mineral_types')

    class Meta:
        db_table = 'mineral_types'


class GeoReference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(unique=True)
    title = models.TextField(blank=True, null=True)
    first_author = models.TextField(blank=True, null=True)
    second_authors = models.TextField(blank=True, null=True)
    journal_name = models.TextField(blank=True, null=True)
    full_text = models.TextField(blank=True, null=True)
    journal_name_2 = models.TextField(blank=True, null=True)
    doi = models.TextField(blank=True, null=True)
    publication_year = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'georeferences'
        ordering = ['id']


# Following are models for easy retrieval of sample-related free-text fields
# from the database.
#
# Though each of these are stored as an ArrayField instances on the samples
# table, the search interface requires a list of all them to filter against;
# we can use these models to accomplish that without an expensive query on the
# the relevant columns of the samples table.
#
# Now, admittedly, this is a denormalization, but I feel that this is a
# reasonable trade-off to get faster GET requests, which is what this
# application will do most of the time.


class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        db_table = 'countries'
        ordering = ['name']


class Region(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        db_table = 'regions'
        ordering = ['name']


class Reference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        db_table = 'references'
        ordering = ['name']


class Collector(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=50)

    class Meta:
        db_table = 'collectors'
        ordering = ['name']

# A mapping table to help the migration of old samples to new samples; can
# be gotten rid of once thi app goes into production.
class SampleMapping(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    old_sample_id = models.IntegerField()
    new_sample_id = models.UUIDField()

    class Meta:
        db_table = 'sample_mapping'

import uuid
from concurrency.fields import AutoIncVersionField

from django.conf import settings
from django.contrib.gis.db import models


class ChemicalAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = AutoIncVersionField()
    public_data = models.BooleanField(default=False)
    reference_x = models.FloatField(blank=True, null=True)
    reference_y = models.FloatField(blank=True, null=True)
    stage_x = models.FloatField(blank=True, null=True)
    stage_y = models.FloatField(blank=True, null=True)
    analysis_method = models.CharField(max_length=50, blank=True, null=True)
    where_done = models.CharField(max_length=50, blank=True, null=True)
    analyst = models.CharField(max_length=50, blank=True, null=True)
    analysis_date = models.DateTimeField(blank=True, null=True)
    date_precision = models.SmallIntegerField(blank=True, null=True)
    description = models.CharField(max_length=1024, blank=True, null=True)
    total = models.FloatField(blank=True, null=True)
    spot_id = models.BigIntegerField()

    subsample = models.ForeignKey('samples.Subsample',
                                  related_name='chemical_analyses')
    mineral = models.ForeignKey('samples.Mineral', blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='chemical_analyses')
    elements = models.ManyToManyField('Element',
                                      through='ChemicalAnalysisElement')
    oxides = models.ManyToManyField('Oxide', through='ChemicalAnalysisOxide')

    # Free-text field; stored as an CharField to avoid joining to the
    # references table every time we retrieve chemical analyses
    reference = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'chemical_analyses'


class Element(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=100)
    alternate_name = models.CharField(max_length=100, blank=True, null=True)
    symbol = models.CharField(unique=True, max_length=4)
    atomic_number = models.IntegerField()
    weight = models.FloatField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'elements'


class Oxide(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    element = models.ForeignKey('Element')
    oxidation_state = models.SmallIntegerField(blank=True, null=True)
    species = models.CharField(unique=True, max_length=20, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    cations_per_oxide = models.SmallIntegerField(blank=True, null=True)
    conversion_factor = models.FloatField()
    order_id = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'oxides'


class ChemicalAnalysisElement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chemical_analysis = models.ForeignKey('ChemicalAnalysis')
    element = models.ForeignKey('Element')
    amount = models.FloatField()
    precision = models.FloatField(blank=True, null=True)
    precision_type = models.CharField(max_length=3, blank=True, null=True)
    measurement_unit = models.CharField(max_length=4, blank=True, null=True)
    min_amount = models.FloatField(blank=True, null=True)
    max_amount = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'chemical_analysis_elements'


class ChemicalAnalysisOxide(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chemical_analysis = models.ForeignKey('ChemicalAnalysis')
    oxide = models.ForeignKey('Oxide')
    amount = models.FloatField()
    precision = models.FloatField(blank=True, null=True)
    precision_type = models.CharField(max_length=3, blank=True, null=True)
    measurement_unit = models.CharField(max_length=4, blank=True, null=True)
    min_amount = models.FloatField(blank=True, null=True)
    max_amount = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'chemical_analysis_oxides'
        unique_together = (('chemical_analysis', 'oxide'),)

import uuid

from django.contrib.gis.db import models


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
        ordering = ['id']


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
        ordering = ['id']
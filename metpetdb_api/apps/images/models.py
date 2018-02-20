# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import uuid

from django.contrib.gis.db import models
from django.dispatch import receiver
from versatileimagefield.fields import VersatileImageField
from versatileimagefield.image_warmer import VersatileImageFieldWarmer
from apps.samples.models import Sample, Subsample
from apps.chemical_analyses.models import ChemicalAnalysis


class ImageContainer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=100, blank=True, null=True)
    url = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'image_container'
        ordering = ('id',)


class Image(models.Model):
    def generate_filename(instance, filename):
        f_hash = str(uuid.uuid4()).replace('-', '')
        assert (len(f_hash) % 2 == 0)
        return "{}{}{}".format(os.sep.join(x + y for x, y in zip(f_hash[::2], f_hash[1::2])),
                               os.sep, filename)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = VersatileImageField('Image', upload_to=generate_filename, blank=True, null=True)
    image_container = models.ForeignKey(ImageContainer, on_delete=models.CASCADE, blank=True, null=True, related_name='images')
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, blank=True, null=True, related_name='images')
    subsample = models.ForeignKey(Subsample, on_delete=models.CASCADE, blank=True, null=True, related_name='images')
    chemical_analysis = models.ForeignKey(ChemicalAnalysis, on_delete=models.CASCADE, blank=True, null=True, related_name='image')

    class Meta:
        db_table = 'images'
        ordering = ('id',)


@receiver(models.signals.post_save, sender=Image)
def warm_images(sender, instance, **kwargs):
    """Create all image size on POST"""
    image_warmer = VersatileImageFieldWarmer(
        instance_or_queryset=instance,
        rendition_key_set='image_sizes',
        image_attr='image'
    )
    image_warmer.warm()

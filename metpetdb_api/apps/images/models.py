# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import uuid

from apps.samples.models import Sample, Subsample
from django.conf import settings
from django.contrib.gis.db import models
from django.dispatch import receiver
from versatileimagefield.fields import VersatileImageField
from versatileimagefield.image_warmer import VersatileImageFieldWarmer


class ImageContainer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=100, blank=True, null=True)
    url = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'image_container'
        ordering = ('id',)


class ImageType(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    image_type = models.CharField(max_length=100, null=False)
    abbreviation = models.CharField(max_length=10)
    comments = models.CharField(max_length=250, null=True, blank=True)


class ImageComments(models.Model):
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment_text = models.TextField(blank=False, null=False)
    version = models.IntegerField(null=False, default=0)
    image = models.ForeignKey('Image', related_name='comments')

    class Meta:
        db_table = 'image_comments'
        ordering = ('comment_id',)


class Image(models.Model):
    def generate_filename(instance, filename):
        f_hash = str(uuid.uuid4()).replace('-', '')
        assert (len(f_hash) % 2 == 0)
        return "{}{}{}".format(os.sep.join(x + y for x, y in zip(f_hash[::2], f_hash[1::2])),
                               os.sep, filename)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = VersatileImageField('Image', upload_to=generate_filename, blank=True, null=True)
    version = models.IntegerField(null=False, default=0)
    scale = models.SmallIntegerField(null=True, blank=True)
    description = models.CharField(max_length=1024, null=True, blank=True)
    image_type = models.ForeignKey(ImageType, null=False, blank=True, default=0)
    collector = models.CharField(max_length=50, blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='images', null=True)
    public_data = models.BooleanField(null=False, default=False)
    image_container = models.ForeignKey(ImageContainer, on_delete=models.CASCADE, blank=True, null=True,
                                        related_name='images')
    # move to respective classes
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, blank=True, null=True, related_name='images')
    subsample = models.ForeignKey(Subsample, on_delete=models.CASCADE, blank=True, null=True, related_name='images')

    class Meta:
        db_table = 'images'
        ordering = ('id',)


class XrayImage(models.Model):
    image = models.OneToOneField(Image, primary_key=True)
    element = models.CharField(max_length=256, blank=True, null=True)
    dwelltime = models.SmallIntegerField(blank=True, null=True)
    current = models.SmallIntegerField(blank=True, null=True)
    voltage = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'xray_image'
        ordering = ('image_id',)

# A mapping table to help migration of old images to new images.
# needed (I think?) for chemical analysis migration.
class ImageMapping(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    old_image_id = models.IntegerField()
    new_image_id = models.UUIDField()

    class Meta:
        db_table = 'image_mapping'


@receiver(models.signals.post_save, sender=Image)
def warm_images(sender, instance, **kwargs):
    """Create all image size on POST"""
    if instance.image:
        image_warmer = VersatileImageFieldWarmer(
            instance_or_queryset=instance,
            rendition_key_set='image_sizes',
            image_attr='image'
        )
        image_warmer.warm()

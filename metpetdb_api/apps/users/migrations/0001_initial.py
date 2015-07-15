# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, blank=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status', default=False)),
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True, editable=False)),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(null=True, max_length=200, blank=True)),
                ('city', models.CharField(null=True, max_length=50, blank=True)),
                ('province', models.CharField(null=True, max_length=100, blank=True)),
                ('country', models.CharField(null=True, max_length=100, blank=True)),
                ('postal_code', models.CharField(null=True, max_length=15, blank=True)),
                ('institution', models.CharField(null=True, max_length=300, blank=True)),
                ('reference_email', models.CharField(null=True, max_length=255, blank=True)),
                ('is_active', models.BooleanField(default=False)),
                ('is_contributor', models.BooleanField(default=False)),
                ('professional_url', models.CharField(null=True, max_length=255, blank=True)),
                ('research_interests', models.CharField(null=True, max_length=1024, blank=True)),
                ('groups', models.ManyToManyField(to='auth.Group', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', verbose_name='groups', related_query_name='user', blank=True)),
                ('user_permissions', models.ManyToManyField(to='auth.Permission', help_text='Specific permissions for this user.', related_name='user_set', verbose_name='user permissions', related_query_name='user', blank=True)),
            ],
            options={
                'db_table': 'users',
            },
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(blank=True, verbose_name='last login', null=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(blank=True, null=True, max_length=200)),
                ('city', models.CharField(blank=True, null=True, max_length=50)),
                ('province', models.CharField(blank=True, null=True, max_length=100)),
                ('country', models.CharField(blank=True, null=True, max_length=100)),
                ('postal_code', models.CharField(blank=True, null=True, max_length=15)),
                ('institution', models.CharField(blank=True, null=True, max_length=300)),
                ('reference_email', models.CharField(blank=True, null=True, max_length=255)),
                ('is_active', models.BooleanField(default=False)),
                ('is_contributor', models.BooleanField(default=False)),
                ('professional_url', models.CharField(blank=True, null=True, max_length=255)),
                ('research_interests', models.CharField(blank=True, null=True, max_length=1024)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_query_name='user', related_name='user_set', verbose_name='groups', to='auth.Group')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_query_name='user', related_name='user_set', verbose_name='user permissions', to='auth.Permission')),
            ],
            options={
                'db_table': 'users',
            },
        ),
    ]

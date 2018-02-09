# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=127)),
                ('last_name', models.CharField(max_length=127)),
                ('gender', models.CharField(blank=True, max_length=1, choices=[(b'F', b'female'), (b'M', b'male')])),
                ('birthday', models.DateField(null=True, blank=True)),
                ('parent', models.CharField(max_length=255, blank=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('phone', models.CharField(max_length=31, blank=True)),
                ('comments', models.TextField(blank=True)),
            ],
            options={
                'ordering': ('last_name', 'first_name'),
            },
        ),
    ]

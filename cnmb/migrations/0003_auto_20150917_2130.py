# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cnmb', '0002_auto_20150806_2245'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.CharField(max_length=255, blank=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('content', models.TextField(blank=True)),
                ('client_viewable', models.BooleanField(default=False)),
                ('navbar_order', models.IntegerField(default=0, blank=True)),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.AlterField(
            model_name='administration',
            name='date_given',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

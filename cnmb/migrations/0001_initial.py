# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Administration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_given', models.DateTimeField(auto_now_add=True)),
                ('comments', models.TextField(blank=True)),
                ('client', models.ForeignKey(to='people.Client')),
            ],
            options={
                'ordering': ('date_given',),
            },
        ),
        migrations.CreateModel(
            name='Definition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('edition', models.CharField(max_length=255, blank=True)),
                ('short_name', models.CharField(max_length=31, blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('date_created',),
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ('section', 'number'),
            },
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.IntegerField()),
                ('description', models.TextField(blank=True)),
                ('item', models.ForeignKey(to='cnmb.Item')),
            ],
            options={
                'ordering': ('item', '-score'),
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField()),
                ('title', models.CharField(max_length=255)),
                ('definition', models.ForeignKey(to='cnmb.Definition')),
            ],
            options={
                'ordering': ('-definition', 'number'),
            },
        ),
        migrations.AddField(
            model_name='item',
            name='section',
            field=models.ForeignKey(to='cnmb.Section'),
        ),
        migrations.AddField(
            model_name='administration',
            name='definition',
            field=models.ForeignKey(to='cnmb.Definition'),
        ),
        migrations.AddField(
            model_name='administration',
            name='examiner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='administration',
            name='scores',
            field=models.ManyToManyField(to='cnmb.Score', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='section',
            unique_together=set([('definition', 'number')]),
        ),
        migrations.AlterUniqueTogether(
            name='item',
            unique_together=set([('section', 'number')]),
        ),
    ]

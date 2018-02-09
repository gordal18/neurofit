# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cnmb.models


class Migration(migrations.Migration):

    dependencies = [
        ('cnmb', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdministrationMedia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('media_file', models.FileField(upload_to=cnmb.models.media_path)),
            ],
            options={
                'ordering': ('administration', 'item'),
                'verbose_name_plural': 'administration media',
            },
        ),
        migrations.RenameField(
            model_name='administration',
            old_name='examiner',
            new_name='trainer',
        ),
        migrations.AddField(
            model_name='administrationmedia',
            name='administration',
            field=models.ForeignKey(to='cnmb.Administration'),
        ),
        migrations.AddField(
            model_name='administrationmedia',
            name='item',
            field=models.ForeignKey(to='cnmb.Item'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('people', '0002_client_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='location_group',
            field=models.ForeignKey(blank=True, to='auth.Group', null=True),
        ),
    ]

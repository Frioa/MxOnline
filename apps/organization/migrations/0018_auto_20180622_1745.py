# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-06-22 17:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0017_auto_20180622_1736'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='org',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='organization.CourseOrg', verbose_name='所属机构'),
        ),
    ]

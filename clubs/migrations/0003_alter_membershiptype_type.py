# Generated by Django 3.2.8 on 2021-11-20 13:34

import clubs.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0002_auto_20211117_1005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membershiptype',
            name='type',
            field=models.CharField(max_length=20, validators=[clubs.models.validate_membership_type]),
        ),
    ]

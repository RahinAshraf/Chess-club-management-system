# Generated by Django 3.2.8 on 2021-11-30 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0016_tournament'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
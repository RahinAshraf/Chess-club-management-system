# Generated by Django 3.2.8 on 2021-12-07 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0023_auto_20211207_1854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]

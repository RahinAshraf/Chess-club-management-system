# Generated by Django 3.2.8 on 2021-11-25 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0007_auto_20211125_1309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membershiptype',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]

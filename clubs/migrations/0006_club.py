# Generated by Django 3.2.8 on 2021-11-25 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0005_alter_membershiptype_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Club',
            fields=[
                ('name', models.CharField(max_length=90, primary_key=True, serialize=False, unique=True)),
                ('location', models.CharField(max_length=100)),
                ('mission_statement', models.CharField(max_length=800)),
            ],
        ),
    ]

# Generated by Django 3.2.5 on 2021-12-09 19:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0030_alter_round_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='score',
            name='tournament',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, to='clubs.tournament'),
            preserve_default=False,
        ),
    ]
# Generated by Django 3.2.8 on 2021-11-25 20:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0013_alter_membershiptype_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='user',
            field=models.ForeignKey(default=6, on_delete=django.db.models.deletion.CASCADE, to='clubs.user'),
            preserve_default=False,
        ),
    ]

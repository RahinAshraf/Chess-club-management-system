# Generated by Django 3.2.8 on 2021-11-25 20:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0014_club_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='club',
            old_name='user',
            new_name='club_owner',
        ),
    ]
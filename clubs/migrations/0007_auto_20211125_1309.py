# Generated by Django 3.2.8 on 2021-11-25 13:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0006_club'),
    ]

    operations = [
        migrations.AddField(
            model_name='membershiptype',
            name='club',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='clubs.club'),
        ),
        migrations.AddField(
            model_name='membershiptype',
            name='id',
            field=models.AutoField(default=1, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='membershiptype',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

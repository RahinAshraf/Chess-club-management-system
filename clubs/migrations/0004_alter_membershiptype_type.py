# Generated by Django 3.2.8 on 2021-11-20 15:16


from django.db import migrations, models
import clubs.models

class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0003_alter_membershiptype_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membershiptype',
            name='type',
            field=models.CharField(max_length=20, validators=[clubs.models.validate_membership_type]),
        ),
    ]
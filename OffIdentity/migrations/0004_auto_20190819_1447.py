# Generated by Django 2.2 on 2019-08-19 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OffIdentity', '0003_offidentity_email_is_valid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offidentity',
            name='email_is_valid',
            field=models.BooleanField(default=True),
        ),
    ]

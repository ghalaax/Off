# Generated by Django 2.2.3 on 2019-07-12 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OffAccount', '0004_auto_20190712_1437'),
    ]

    operations = [
        migrations.AddField(
            model_name='offaccount',
            name='system_account',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 2.2.5 on 2019-10-03 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elements', '0005_auto_20190930_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='element',
            name='data_checksum',
            field=models.BinaryField(max_length=64, null=True),
        ),
    ]

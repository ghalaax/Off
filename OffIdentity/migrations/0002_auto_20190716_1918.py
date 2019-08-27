# Generated by Django 2.2 on 2019-07-16 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OffIdentity', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='offidentity',
            index=models.Index(fields=['-creation_date'], name='OffIdentity_creatio_7bbfa0_idx'),
        ),
        migrations.AddIndex(
            model_name='offidentity',
            index=models.Index(fields=['key'], name='OffIdentity_key_c043e0_idx'),
        ),
    ]

# Generated by Django 2.2.4 on 2019-09-07 01:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elements', '0007_auto_20190907_0126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elementmetadata',
            name='element',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='metadata', to='elements.Element'),
        ),
    ]

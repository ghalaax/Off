# Generated by Django 2.2 on 2019-09-05 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transtype',
            field=models.CharField(choices=[('CREATION', 'Création'), ('EXCHANGE', 'Échange')], max_length=10),
        ),
    ]

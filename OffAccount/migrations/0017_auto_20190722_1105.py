# Generated by Django 2.2 on 2019-07-22 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OffAccount', '0016_auto_20190721_1733'),
    ]

    operations = [
        migrations.CreateModel(
            name='OffBlock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='offcreditcreation',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='offtransaction',
            name='creation',
        ),
        migrations.RemoveField(
            model_name='offtransaction',
            name='credit',
        ),
        migrations.AddField(
            model_name='offtransaction',
            name='transtype',
            field=models.CharField(choices=[('CREATION', 'CREATION'), ('EXCHANGE', 'EXCHANGE')], default='CREATION', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='offtransaction',
            name='value',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='OffCredit',
        ),
        migrations.DeleteModel(
            name='OffCreditCreation',
        ),
    ]

# Generated by Django 2.2.5 on 2019-09-27 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elements', '0002_userelement'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='elementlink',
            unique_together={('subject', 'object')},
        ),
        migrations.RemoveField(
            model_name='elementlink',
            name='link',
        ),
        migrations.DeleteModel(
            name='Linker',
        ),
    ]
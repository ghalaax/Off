# Generated by Django 2.2.4 on 2019-09-06 12:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('elements', '0003_auto_20190906_1236'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Community',
            fields=[
                ('element_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='elements.Element')),
            ],
            bases=('elements.element',),
        ),
        migrations.CreateModel(
            name='CommunityPart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part_on', models.DateTimeField(auto_now_add=True)),
                ('alive', models.BooleanField(default=True)),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='communities.Community')),
                ('federate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='community',
            name='federates',
            field=models.ManyToManyField(through='communities.CommunityPart', to=settings.AUTH_USER_MODEL),
        ),
    ]
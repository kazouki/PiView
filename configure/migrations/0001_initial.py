# Generated by Django 2.2 on 2019-04-04 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=70)),
                ('url', models.CharField(max_length=1000)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
    ]

# Generated by Django 2.2.2 on 2019-08-03 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CDriveUser',
            fields=[
                ('username', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=70)),
                ('firstname', models.CharField(max_length=50)),
                ('lastname', models.CharField(max_length=50)),
            ],
        ),
    ]

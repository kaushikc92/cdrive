# Generated by Django 2.2 on 2019-05-18 16:57

from django.db import migrations, models
import drive_api.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CDriveFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cdrive_file', models.FileField(upload_to=drive_api.models.file_path)),
                ('file_name', models.CharField(max_length=200)),
                ('file_owner', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='CDriveUser',
            fields=[
                ('username', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=70)),
                ('firstname', models.CharField(max_length=50)),
                ('lastname', models.CharField(max_length=50)),
                ('shared_files', models.ManyToManyField(to='drive_api.CDriveFile')),
            ],
        ),
    ]

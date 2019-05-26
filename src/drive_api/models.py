from django.db import models
from django.conf import settings

# Create your models here.
def file_path(instance, filename):
    if settings.DEBUG_LOCAL:
        return 'localhost/{0}/{1}'.format(instance.file_owner, filename)
    else:
        return '{0}/{1}'.format(instance.file_owner, filename)

# Create your models here.
class CDriveFile(models.Model):
    cdrive_file = models.FileField(upload_to=file_path, blank=False, null=False)
    file_name = models.CharField(max_length=200)
    file_owner = models.CharField(max_length=200)
    file_size = models.IntegerField()

class CDriveApplication(models.Model):
    app_name = models.CharField(max_length=200)
    app_url = models.URLField(max_length=200)
    app_image_url = models.CharField(max_length=200)

class CDriveUser(models.Model):
    username = models.CharField(max_length=50, primary_key=True)
    email = models.EmailField(max_length=70)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    shared_files = models.ManyToManyField(CDriveFile)
    installed_apps = models.ManyToManyField(CDriveApplication)


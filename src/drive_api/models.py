from django.db import models

# Create your models here.
def user_directory_path(instance, filename):
    return '{0}/{1}'.format(instance.file_owner, filename)

# Create your models here.
class CDriveFile(models.Model):
    cdrive_file = models.FileField(upload_to=user_directory_path, blank=False, null=False)
    file_name = models.CharField(max_length=200)
    file_owner = models.CharField(max_length=200)

class CDriveUser(models.Model):
    username = models.CharField(max_length=50, primary_key=True)
    email = models.EmailField(max_length=70)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    shared_files = models.ManyToManyField(CDriveFile)

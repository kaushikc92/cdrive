from django.db import models
from django.conf import settings

def file_path(instance, filename):
    folder = instance.parent
    path = filename
    while folder is not None:
        path = folder.name + '/' + path
        folder = folder.parent
    return path

class CDriveFolder(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='%(class)s_parent')
    owner = models.ForeignKey('user_mgmt.CDriveUser', on_delete=models.CASCADE, null=True, related_name='%(class)s_owner' )

class CDriveFile(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('CDriveFolder', on_delete=models.CASCADE, related_name='%(class)s_parent') 
    cdrive_file = models.FileField(upload_to=file_path, blank=False, null=False)
    size = models.IntegerField()
    owner = models.ForeignKey('user_mgmt.CDriveUser', on_delete=models.CASCADE, related_name='%(class)s_owner' )

class FilePermission(models.Model):
    PERMISSIONS = (
        ('V', 'View'),
        ('E', 'Edit'),
    )
    cdrive_file = models.ForeignKey('CDriveFile', on_delete=models.CASCADE, related_name='%(class)s_file')
    user = models.ForeignKey('user_mgmt.CDriveUser', on_delete=models.CASCADE, related_name='%(class)s_user')
    app = models.ForeignKey('apps_api.CDriveApplication', on_delete=models.CASCADE, related_name='%(class)s_app')
    permission = models.CharField(max_length=1, choices=PERMISSIONS)

class FolderPermission(models.Model):
    PERMISSIONS = (
        ('V', 'View'),
        ('E', 'Edit'),
    )
    cdrive_folder = models.ForeignKey('CDriveFolder', on_delete=models.CASCADE, related_name='%(class)s_folder')
    user = models.ForeignKey('user_mgmt.CDriveUser', on_delete=models.CASCADE, related_name='%(class)s_user')
    app = models.ForeignKey('apps_api.CDriveApplication', on_delete=models.CASCADE, related_name='%(class)s_app')
    permission = models.CharField(max_length=1, choices=PERMISSIONS)

from django.db import models
from django.conf import settings
from user_mgmt.models import CDriveUser
from apps_api.models import CDriveApplication

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
    owner = models.ForeignKey(CDriveUser, on_delete=models.CASCADE, null=True, related_name='%(class)s_owner' )
    edit_user = models.ManyToManyField(CDriveUser, related_name='%(class)s_edit_user')
    view_user = models.ManyToManyField(CDriveUser, related_name='%(class)s_view_user')
    share_user = models.ManyToManyField(CDriveUser, related_name='%(class)s_share_user')
    edit_app = models.ManyToManyField(CDriveApplication, related_name='%(class)s_edit_app')
    view_app = models.ManyToManyField(CDriveApplication, related_name='%(class)s_view_app')
    share_app = models.ManyToManyField(CDriveApplication, related_name='%(class)s_share_app')

class CDriveFile(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('CDriveFolder', on_delete=models.CASCADE, related_name='%(class)s_parent') 
    cdrive_file = models.FileField(upload_to=file_path, blank=False, null=False)
    size = models.IntegerField()
    owner = models.ForeignKey(CDriveUser, on_delete=models.CASCADE, related_name='%(class)s_owner' )
    edit_user = models.ManyToManyField(CDriveUser, related_name='%(class)s_edit_user')
    view_user = models.ManyToManyField(CDriveUser, related_name='%(class)s_view_user')
    share_user = models.ManyToManyField(CDriveUser, related_name='%(class)s_share_user')
    edit_app = models.ManyToManyField(CDriveApplication, related_name='%(class)s_edit_app')
    view_app = models.ManyToManyField(CDriveApplication, related_name='%(class)s_view_app')
    share_app = models.ManyToManyField(CDriveApplication, related_name='%(class)s_share_app')

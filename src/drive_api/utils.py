from .models import CDriveFolder, CDriveFile, FolderPermission, FilePermission
from apps_api.models import CDriveApplication
from django.conf import settings

def get_object_by_path(path):
    tokens = path.split('/')
    parent = None
    for token in tokens:
        queryset = CDriveFolder.objects.filter(parent=parent, name=token)
        if queryset.exists():
            parent = queryset[0]
        else:
            parent = CDriveFile.objects.get(parent=parent, name=token)
    return parent

def initialize_user_drive(cDriveUser):
    home_folder = CDriveFolder.objects.filter(name='Home', parent=None, owner=None)[0]
    cDriveFolder = CDriveFolder(
        name = cDriveUser.username,
        parent = home_folder,
        owner = cDriveUser
    )
    cDriveFolder.save()
    cDriveApp = CDriveApplication(
        name = 'cdrive',
        client_id = settings.COLUMBUS_CLIENT_ID,
        client_secret = settings.COLUMBUS_CLIENT_SECRET,
        owner = cDriveUser
    )
    cDriveApp.save()
    permission = FolderPermission(
        cdrive_folder = home_folder,
        user = cDriveUser,
        app = cDriveApp,
        permission = 'V'
    )
    permission.save()

def check_permission(cDriveObject, cDriveUser, cDriveApp, permission):
    if cDriveUser is None or cDriveApp is None or cDriveObject is None:
        return False
    elif cDriveObject.owner == cDriveUser and cDriveApp.name == 'cdrive':
        return True
    elif cDriveObject.__class__.__name__ == 'CDriveFolder':
        return FolderPermission.objects.filter(
            cdrive_folder = cDriveObject,
            user = cDriveUser,
            app = cDriveApp,
            permission = permission
        ).exists()
    else:
        return FilePermission.objects.filter(
            cdrive_file = cDriveObject,
            user = cDriveUser,
            app = cDriveApp,
            permission = permission
        ).exists()

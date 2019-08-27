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
    home_folder = CDriveFolder.objects.filter(name='users', parent=None, owner=None)[0]
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

def check_folder_permission(cDriveFolder, cDriveUser, cDriveApp, permission):
    return FolderPermission.objects.filter(
        cdrive_folder = cDriveFolder,
        user = cDriveUser,
        app = cDriveApp,
        permission = permission).exists()

def check_file_permission(cDriveFile, cDriveUser, cDriveApp, permission):
    return FilePermission.objects.filter(
        cdrive_file = cDriveFile,
        user = cDriveUser,
        app = cDriveApp,
        permission = permission).exists()

def check_permission_recursive(cDriveObject, cDriveUser, cDriveApp, permission):
    if (cDriveObject.__class__.__name__ == 'CDriveFolder'
        and check_folder_permission(cDriveObject, cDriveUser, cDriveApp, permission)):
        return True
    if (cDriveObject.__class__.__name__ == 'CDriveFile'
        and  check_file_permission(cDriveObject, cDriveUser, cDriveApp, permission)):
        return True
    parent = cDriveObject.parent
    if parent is None:
        return False
    else:
        return check_permission_recursive(parent, cDriveUser, cDriveApp, permission)

def check_permission(cDriveObject, cDriveUser, cDriveApp, permission):
    if cDriveUser is None or cDriveApp is None or cDriveObject is None:
        return False
    if cDriveObject.owner == cDriveUser and cDriveApp.name == 'cdrive':
        return True
    if check_permission_recursive(cDriveObject, cDriveUser, cDriveApp, 'E'):
        return True
    if permission == 'V' and check_permission_recursive(cDriveObject, cDriveUser, cDriveApp, 'V'):
        return True
    return False

def check_child_permission(cDriveFolder, cDriveUser, cDriveApp):
    files = CDriveFile.objects.filter(parent=cDriveFolder)
    for f in files:
        if (check_file_permission(f, cDriveUser, cDriveApp, 'E')
            or check_file_permission(f, cDriveUser, cDriveApp, 'V')):
            return True
    folders = CDriveFolder.objects.filter(parent=cDriveFolder)
    for f in folders:
        if (check_folder_permission(f, cDriveUser, cDriveApp, 'E')
            or check_folder_permission(f, cDriveUser, cDriveApp, 'V')
            or check_child_permission(f, cDriveUser, cDriveApp)):
            return True
    return False

def delete_folder(cDriveFolder):
    CDriveFile.objects.filter(parent=cDriveFolder).delete()
    children = CDriveFolder.objects.filter(parent=cDriveFolder)
    for child in children:
        delete_folder(child)
    cDriveFolder.delete()

def share_object(cdrive_object, target_user, target_app, permission):
    if cdrive_object.__class__.__name__ == 'CDriveFile':
        file_permission = FilePermission(
            cdrive_file = cdrive_object,
            user = target_user,
            app = target_app,
            permission = permission
        )
        file_permission.save()
    else :
        folder_permission = FolderPermission(
            cdrive_folder = cdrive_object,
            user = target_user,
            app = target_app,
            permission = permission
        )
        folder_permission.save()

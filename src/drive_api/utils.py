from .models import CDriveFolder, CDriveFile

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
    query = CDriveFolder.objects.filter(name='Home', parent=None, owner=None)
    home_folder = None
    if query.exists():
        home_folder = query[0]
    else:
        home_folder = CDriveFolder(
            name = 'Home',
            parent = None,
            owner = None
        )
        home_folder.save()
        home_folder = CDriveFolder.objects.filter(name='Home', parent=None, owner=None)[0]

    cDriveFolder = CDriveFolder(
        name = cDriveUser.username,
        parent = home_folder,
        owner = cDriveUser
    )
    cDriveFolder.save()
    cDriveFolder.view_user.add(cDriveUser)
    cDriveFolder.edit_user.add(cDriveUser)
    cDriveFolder.share_user.add(cDriveUser)

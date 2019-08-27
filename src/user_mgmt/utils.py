from .models import CDriveUser
from apps_api.models import CDriveApplication
import requests

def introspect_token(request):
    auth_header = request.META['HTTP_AUTHORIZATION']
    token = auth_header.split()[1] 
    url = 'http://authentication/o/introspect/'
    response = requests.post(
        url=url,
        data={'token': token}, 
        headers={'Authorization': auth_header}
    )
    cDriveUser = None
    cDriveApp = None
    if response.status_code == 200:
        if 'username' in response.json():
            cDriveUser = get_user(response.json()['username'])
        if 'client_id' in response.json():
            cDriveApp = get_app_from_id(response.json()['client_id'], cDriveUser)
    return cDriveUser, cDriveApp

def get_app_from_id(client_id, owner):
    app_query = CDriveApplication.objects.filter(client_id=client_id, owner=owner)
    if app_query.exists():
        return app_query[0]
    else:
        return None

def get_app(app_name, owner):
    app_query = CDriveApplication.objects.filter(name=app_name, owner=owner)
    if app_query.exists():
        return app_query[0]
    else:
        return None

def get_user(username):
    queryset = CDriveUser.objects.filter(username=username)
    if queryset.exists():
        return queryset[0]
    else :
        return None

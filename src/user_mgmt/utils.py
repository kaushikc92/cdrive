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
    cDriveUser = get_user(response.json())
    cDriveApp = get_application(response.json())
    return cDriveUser, cDriveApp

def get_application(json_data):
    if 'client_id' in json_data:
        client_id = json_data['client_id']
        app_query = CDriveApplication.objects.filter(client_id=client_id)
        if app_query.exists():
            return app_query[0]
        else:
            return None
    else:
        return None

def get_user(json_data):
    if 'username' in json_data:
        username = json_data['username']
        cDriveUser = CDriveUser.objects.filter(username=username)[0]
        return cDriveUser
    else :
        return None

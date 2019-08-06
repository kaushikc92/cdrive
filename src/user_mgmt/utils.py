from .models import CDriveUser
import requests

def get_user(request):
    auth_header = request.META['HTTP_AUTHORIZATION']
    token = auth_header.split()[1] 
    url = 'http://authentication/o/introspect/'
    response = requests.post(
        url=url,
        data={'token': token}, 
        headers={'Authorization': auth_header}
    )
    if response.status_code == 200 and 'username' in response.json():
        username = response.json()['username']
        cDriveUser = CDriveUser.objects.filter(username=username)[0]
        return cDriveUser
    else :
        return None

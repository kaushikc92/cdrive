from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import requests

from user_mgmt.utils import introspect_token
from .models import CDriveApplication
from .serializers import CDriveApplicationSerializer

# Create your views here.
class InstallApplicationView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        cDriveUser, cDriveApp = introspect_token(request)
        username = cDriveUser.username
        app_docker_link = request.data['app_docker_link']
        start_index = app_docker_link.rfind('/')
        end_index = app_docker_link.rfind(':')
        if end_index == -1:
            end_index = len(app_docker_link)
        app_name = app_docker_link[start_index + 1 : end_index]

        data = {
                'app_name': app_name,
                'redirect_url': settings.APPS_ROOT + username + '/' + app_name + '/'
        }

        response = requests.post(url='http://authentication/register-app/', data=data)

        data = response.json()
        client_id = data['clientId']
        client_secret = data['clientSecret']
        
        data = {
                'imagePath': app_docker_link,
                'username': username,
                'appName': app_name,
                'clientId': client_id,
                'clientSecret': client_secret
        }
        response = requests.post(url='http://app-manager/start-app', data=data)
        
        cDriveApplication = CDriveApplication(
                name = app_name,
                url = settings.APPS_ROOT + username + '/' + app_name + '/',
                image = app_docker_link,
                owner = cDriveUser,
                client_id = client_id,
                client_secret = client_secret
        )
        cDriveApplication.save()

        return Response({'appName': app_name}, status=status.HTTP_201_CREATED)

class StartApplicationView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        cDriveUser, cDriveApp = introspect_token(request)
        username = cDriveUser.username
        app_name = request.data['app_name']

        cDriveApplication = CDriveApplication.objects.filter(owner=cDriveUser, name=app_name)[0]
        
        data = {
                'imagePath': cDriveApplication.image,
                'username': username,
                'appName': app_name,
                'clientId': cDriveApplication.client_id,
                'clientSecret': cDriveApplication.client_secret
        }
        response = requests.post(url='http://app-manager/start-app', data=data)

        return Response(status=status.HTTP_200_OK)

class AppStatusView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request):
        cDriveUser, cDriveApp = introspect_token(request)
        username = cDriveUser.username
        app_name = request.query_params['app_name']

        response = requests.get(url='http://app-manager/get-app-status/' + username + '/' + app_name + '/')
        data = response.json()

        return Response({'appStatus': data['appStatus']})

class DeleteApplicationView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        cDriveUser, cDriveApp = introspect_token(request)
        username = cDriveUser.username
        app_name = request.data['app_name']
        data = {
                'username': username,
                'appName': app_name
        }
        response = requests.post(url='http://app-manager/stop-app', data=data)
        response = requests.post(url='http://app-manager/delete-app-storage', data=data)
        CDriveApplication.objects.filter(owner=username, name=app_name).delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class StopApplicationsView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        cDriveUser, cDriveApp = introspect_token(request)
        username = cDriveUser.username
        apps = CDriveApplication.objects.filter(owner=username)
        for app in apps:
            data = {
                    'username': username,
                    'appName': app.name
            }
            response = requests.post(url='http://app-manager/stop-app', data=data)
        return Response(status=status.HTTP_200_OK)

class ApplicationsListView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request):
        cDriveUser, cDriveApp = introspect_token(request)
        queryset = CDriveApplication.objects.filter(owner=cDriveUser).exclude(name='cdrive')
        serializer = CDriveApplicationSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

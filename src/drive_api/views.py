from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from rest_framework.parsers import FileUploadParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import requests

import boto3
from botocore.client import Config

from .models import CDriveFile, CDriveUser, CDriveApplication
from .serializers import CDriveFileSerializer, CDriveUserSerializer, CDriveApplicationSerializer

# Create your views here.

class CDriveBaseView(APIView):
    @staticmethod
    def get_name(request):
        auth_header = request.META['HTTP_AUTHORIZATION']
        token = auth_header.split()[1] 
        if settings.DEBUG_LOCAL:
            url = 'http://0.0.0.0:8000/o/introspect/'
        else:
            url = 'http://authentication/o/introspect/'
        response = requests.post(
            url=url,
            data={'token': token}, 
            headers={'Authorization': auth_header}
        )
        username = response.json()['username']
        return username

class FileUploadView(CDriveBaseView):
    parser_class = (FileUploadParser,)

    @csrf_exempt
    def post(self, request, format=None):
        username = FileUploadView.get_name(request) 
        cDriveFile = CDriveFile(
            cdrive_file = request.data['file'],
            file_name = request.data['file'].name,
            file_owner = username,
            file_size = request.data['file'].size
        )
        cDriveFile.save()
        return Response({'file_name':request.data['file'].name}, status=status.HTTP_201_CREATED)

class ListFilesView(CDriveBaseView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request, format=None):
        username = ListFilesView.get_name(request)
        queryset = CDriveFile.objects.filter(file_owner=username)
        serializer = CDriveFileSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DeleteFileView(CDriveBaseView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def delete(self, request, format=None):
        username = DeleteFileView.get_name(request) 
        file_name = request.query_params['file_name']
        CDriveFile.objects.filter(file_name=file_name, file_owner=username).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DownloadUrlView(CDriveBaseView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request, format=None):
        username = DownloadUrlView.get_name(request) 
        file_name = request.query_params['file_name']
        client = boto3.client(
            's3', 
            region_name = 'us-east-1',
            config=Config(signature_version='s3v4'),
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        if settings.DEBUG_LOCAL:
            object_key = 'localhost' + '/' + username + '/' + file_name
        else:
            object_key = username + '/' + file_name
        url = client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': object_key
            },
            ExpiresIn=3600
        )
        return Response({'download_url':url})

class FileContentView(CDriveBaseView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request, format=None):
        username = FileContentView.get_name(request) 
        file_name = request.query_params['file_name']
        content = CDriveFile.objects.filter(file_name=file_name, file_owner=username)[0].cdrive_file.read()
        return Response(content)

class UserDetailsView(CDriveBaseView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request, format=None):
        username = UserDetailsView.get_name(request) 
        query_set = CDriveUser.objects.filter(username=username)
        if not query_set:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user_data = query_set[0]
        serializer = CDriveUserSerializer(user_data)
        return Response(serializer.data, status=200)

class SharedFilesListView(CDriveBaseView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request, format=None):
        username = SharedFilesListView.get_name(request)
        queryset = CDriveUser.objects.filter(username=username)[0].shared_files.all()
        serializer = CDriveFileSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

class DownloadSharedFileView(CDriveBaseView):
    parser_class = (JSONParser,)
    
    @csrf_exempt
    def get(self, request, format=None):
        username = DownloadSharedFileView.get_name(request)
        file_name = request.query_params['file_name']
        file_owner = request.query_params['file_owner']

        shared_files_list = CDriveUser.objects.filter(username=username)[0].shared_files.all()

        queryset = shared_files_list.filter(file_name=file_name, file_owner=file_owner)

        if not queryset.exists():
            return Response(status=400)

        client = boto3.client(
            's3', 
            region_name = 'us-east-1',
            config=Config(signature_version='s3v4'),
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        if settings.DEBUG_LOCAL:
            object_key = 'localhost' + '/' + file_owner + '/' + file_name
        else:
            object_key = file_owner + '/' + file_name
        url = client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': object_key
            },
            ExpiresIn=3600
        )
        return Response({'download_url':url})

class ShareFileView(CDriveBaseView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request, format=None):
        username = ShareFileView.get_name(request)
        file_name = request.data['file_name']
        target_user_email = request.data['share_with']

        query = CDriveUser.objects.filter(email=target_user_email)
        if query.exists():
            cDriveFile = CDriveFile.objects.filter(file_name=file_name, file_owner=username)[0]
            query[0].shared_files.add(cDriveFile)

        return Response(status=201)

class InstallApplicationView(CDriveBaseView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        username = InstallApplicationView.get_name(request)
        app_docker_link = request.data['app_docker_link']
        start_index = app_docker_link.rfind('/')
        end_index = app_docker_link.rfind(':')
        if end_index == -1:
            end_index = len(app_docker_link)
        app_name = app_docker_link[start_index + 1 : end_index]

        data = {
                'app_name': app_name,
                'redirect_url': settings.APPS_ROOT + username + '/' + app_name
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
                url = settings.APPS_ROOT + username + '/' + app_name,
                image = app_docker_link,
                owner = username,
                client_id = client_id,
                client_secret = client_secret
        )
        cDriveApplication.save()

        return Response({'appName': app_name}, status=status.HTTP_201_CREATED)

class StartApplicationView(CDriveBaseView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        username = StartApplicationView.get_name(request)
        app_name = request.data['app_name']

        cDriveApplication = CDriveApplication.objects.filter(owner=username, name=app_name)[0]
        
        data = {
                'imagePath': cDriveApplication.image,
                'username': username,
                'appName': app_name,
                'clientId': cDriveApplication.client_id,
                'clientSecret': cDriveApplication.client_secret
        }
        response = requests.post(url='http://app-manager/start-app', data=data)

        return Response(status=status.HTTP_201_CREATED)

class AppStatusView(CDriveBaseView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request):
        username = AppStatusView.get_name(request)
        app_name = request.query_params['app_name']

        response = requests.get(url='http://app-manager/get-app-status/' + username + '/' + app_name + '/')
        data = response.json()

        return Response({'appStatus': data['appStatus']})

class DeleteApplicationView(CDriveBaseView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        username = DeleteApplicationView.get_name(request)
        app_name = request.data['app_name']
        data = {
                'username': username,
                'appName': app_name
        }
        response = requests.post(url='http://app-manager/stop-app', data=data)
        response = requests.post(url='http://app-manager/delete-app-storage', data=data)
        CDriveApplication.objects.filter(owner=username, name=app_name).delete()
        
        return Response(status=201)

class StopApplicationsView(CDriveBaseView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        username = StopApplicationsView.get_name(request)
        apps = CDriveApplication.objects.filter(owner=username)
        for app in apps:
            data = {
                    'username': username,
                    'appName': app.name
            }
            response = requests.post(url='http://app-manager/stop-app', data=data)
        return Response(status=201)

class ApplicationsListView(CDriveBaseView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request):
        username = ApplicationsListView.get_name(request)
        queryset = CDriveApplication.objects.filter(owner=username)
        serializer = CDriveApplicationSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

class RegisterUserView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request, format=None):
        serializer = CDriveUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=201)
        else:
            return Response(status=400)

class ClientIdView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request, format=None):
        data = {'client_id': settings.COLUMBUS_CLIENT_ID}
        return Response(data, status=status.HTTP_200_OK)

class AuthenticationTokenView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request, format=None):
        code = request.data['code']
        redirect_uri = request.data['redirect_uri']
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': settings.COLUMBUS_CLIENT_ID,
            'client_secret': settings.COLUMBUS_CLIENT_SECRET
        }
        if settings.DEBUG_LOCAL:
            response = requests.post(url='http://0.0.0.0:8000/o/token/', data=data)
        else:
            response = requests.post(url='http://authentication/o/token/', data=data)

        return Response(response.json(), status=response.status_code)

class LogoutView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        auth_header = request.META['HTTP_AUTHORIZATION']
        token = auth_header.split()[1] 
        data = {
            'token': token,
            'client_id': settings.COLUMBUS_CLIENT_ID,
            'client_secret': settings.COLUMBUS_CLIENT_SECRET
        }
        if settings.DEBUG_LOCAL:
            response = requests.post(url='http://0.0.0.0:8000/o/revoke_token/', data=data)
        else:
            response = requests.post(url='http://authentication/o/revoke_token/', data=data)
        return Response(status=response.status_code)

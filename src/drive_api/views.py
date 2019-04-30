from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import FileUploadParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import requests
import pdb

# Create your views here.

class CDriveBaseView(APIView):
    @staticmethod
    def get_name(request):
        auth_header = request.META['HTTP_AUTHORIZATION']
        token = auth_header.split()[1] 
        response = requests.post(
            url='http://0.0.0.0:8000/o/introspect/', 
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
        return Response({'file_name':request.data['file'].name, 'username': username}, status=status.HTTP_201_CREATED)

class ListFilesView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request, format=None):
        username = ListFilesView.get_name(request)
        return Response({'foo':'bar'}, status=status.HTTP_200_OK)

from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import FileUploadParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

# Create your views here.
class FileUploadView(APIView):
    parser_class = (FileUploadParser,)

    @csrf_exempt
    def post(self, request, format=None):
        return Response({'file_name':request.data['file'].name}, status=status.HTTP_201_CREATED)

class ListFilesView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request, format=None):
        return Response({'foo':'bar'}, status=status.HTTP_200_OK)

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import requests

from .models import CDriveUser
from .serializers import CDriveUserSerializer

from drive_api.utils import initialize_user_drive
from .utils import introspect_token

class UserDetailsView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request, format=None):
        user, app = introspect_token(request)
        if user is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else :
            serializer = CDriveUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

class RegisterUserView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request, format=None):
        serializer = CDriveUserSerializer(data=request.data)
        if serializer.is_valid():
            cDriveUser = serializer.save()
            initialize_user_drive(cDriveUser)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

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
        response = requests.post(url='http://authentication/o/revoke_token/', data=data)
        return Response(status=response.status_code)

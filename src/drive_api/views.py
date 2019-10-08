from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from rest_framework.parsers import FileUploadParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import boto3
from botocore.client import Config

import csv, io

from user_mgmt.utils import introspect_token, get_user, get_app

from .models import CDriveFile, CDriveFolder, FilePermission, FolderPermission
from .serializers import CDriveFileSerializer, CDriveFolderSerializer
from .utils import *

class UploadView(APIView):
    parser_class = (FileUploadParser,)

    @csrf_exempt
    def post(self, request):
        cDriveUser, cDriveApp = introspect_token(request)

        path = request.data['path']
        parent = get_object_by_path(path)

        if check_permission(parent, cDriveUser, cDriveApp, 'E'):
            cDriveFile = CDriveFile(
                cdrive_file = request.data['file'],
                name = request.data['file'].name,
                owner = cDriveUser,
                parent = parent,
                size = request.data['file'].size
            )
            cDriveFile.save()
            return Response({'file_name':request.data['file'].name}, status=status.HTTP_201_CREATED)
        else :
            return Response(status=status.HTTP_403_FORBIDDEN)

class InitiateChunkedUpload(APIView):
    parser_class = (JSONParser,)

    def post(self, request):
        cDriveUser, cDriveApp = introspect_token(request)
        
        path = request.data['path']
        file_name = request.data['file_name']
        
        parent = get_object_by_path(path)

        key = path + '/' + file_name

        if check_permission(parent, cDriveUser, cDriveApp, 'E'):
            client = boto3.client(
                's3',
                region_name = 'us-east-1',
                config=Config(signature_version='s3v4'),
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )

            mpu = client.create_multipart_upload(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)

            return Response({'uploadId': mpu['UploadId']}, status=status.HTTP_200_OK)
        else :
            return Response(status=status.HTTP_403_FORBIDDEN)

class UploadChunk(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request):
        cDriveUser, cDriveApp = introspect_token(request)

        if cDriveUser is None:
            return Response(status=status.HTTP_403_FORBIDDEN)

        path = request.data['path']
        file_name = request.data['file_name']
        part_number = int(request.data['partNumber'])
        upload_id = request.data['uploadId']
        chunk_data = request.data['chunk']

        key = path + '/' + file_name

        client = boto3.client(
            's3',
            region_name = 'us-east-1',
            config=Config(signature_version='s3v4'),
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        part_info = client.upload_part(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=key,
            PartNumber=part_number,
            UploadId=upload_id,
            Body=chunk_data
        )

        etag = part_info['ETag'].strip('\"')

        return Response({'ETag': etag}, status=status.HTTP_200_OK)

class CompleteChunkedUpload(APIView):
    parser_class = (JSONParser,)

    def post(self, request):
        cDriveUser, cDriveApp = introspect_token(request)

        path = request.data['path']
        file_name = request.data['file_name']
        upload_id = request.data['uploadId']
        parts = request.data['partInfo']
        size = request.data['size']
        
        part_info = { 'Parts': [] }
        parts = parts.split(',')
        for i, part in enumerate(parts, start=1):
            info = { 'ETag': part, 'PartNumber': i }
            part_info['Parts'].append(info)

        key = path + '/' + file_name

        client = boto3.client(
            's3',
            region_name = 'us-east-1',
            config=Config(signature_version='s3v4'),
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        client.complete_multipart_upload(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=key,
            UploadId=upload_id,
            MultipartUpload=part_info
        )

        parent = get_object_by_path(path)

        if check_permission(parent, cDriveUser, cDriveApp, 'E'):
            cDriveFile = CDriveFile(
                cdrive_file = path + '/' + file_name,
                name = file_name,
                owner = cDriveUser,
                parent = parent,
                size = size
            )
            cDriveFile.save()
            return Response({'file_name':file_name}, status=status.HTTP_201_CREATED)
        else :
            return Response(status=status.HTTP_403_FORBIDDEN)

class CreateView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        cDriveUser, cDriveApp = introspect_token(request)

        path = request.data['path']
        name = request.data['name']

        parent = get_object_by_path(path)

        if check_permission(parent, cDriveUser, cDriveApp, 'E'):
            cDriveFolder = CDriveFolder(
                name = name,
                owner = cDriveUser,
                parent = parent
            )
            cDriveFolder.save()
            return Response({'name': name}, status=status.HTTP_201_CREATED)
        else :
            return Response(status=status.HTTP_403_FORBIDDEN)

class ListView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request):
        cDriveUser, cDriveApp = introspect_token(request)

        path = request.query_params['path']
        parent = get_object_by_path(path)

        data = {}

        if check_permission(parent, cDriveUser, cDriveApp, 'E'):
            data['permission'] = 'Edit'
        else: 
            data['permission'] = 'View'
        
        data['driveObjects'] = []
        folders = CDriveFolder.objects.filter(parent=parent)
        for f in folders:
            ser = CDriveFolderSerializer(f).data
            if check_permission(f, cDriveUser, cDriveApp, 'E'):
                ser['permission'] = 'Edit'
                ser['type'] = 'Folder'
                data['driveObjects'].append(ser)
            elif check_permission(f, cDriveUser, cDriveApp, 'V'):
                ser['permission'] = 'View'
                ser['type'] = 'Folder'
                data['driveObjects'].append(ser)
            elif check_child_permission(f, cDriveUser, cDriveApp):
                ser['permission'] = 'View'
                ser['type'] = 'Folder'
                data['driveObjects'].append(ser)

        files = CDriveFile.objects.filter(parent=parent)
        for f in files:
            ser = CDriveFileSerializer(f).data
            if check_permission(f, cDriveUser, cDriveApp, 'E'):
                ser['permission'] = 'Edit'
                ser['type'] = 'File'
                data['driveObjects'].append(ser)
            elif check_permission(f, cDriveUser, cDriveApp, 'V'):
                ser['permission'] = 'View'
                ser['type'] = 'File'
                data['driveObjects'].append(ser)

        return Response(data, status=status.HTTP_200_OK)

class DeleteView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def delete(self, request):
        cDriveUser, cDriveApp = introspect_token(request)
        
        path = request.query_params['path']
        cDriveObject = get_object_by_path(path)
        
        if check_permission(cDriveObject, cDriveUser, cDriveApp, 'E'):
            if cDriveObject.__class__.__name__ == 'CDriveFolder':
                delete_folder(cDriveObject)
            else :
                cDriveObject.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else :
            return Response(status=status.HTTP_403_FORBIDDEN)

class DownloadView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request):
        cDriveUser, cDriveApp = introspect_token(request)
        
        path = request.query_params['path']
        cDriveObject = get_object_by_path(path)

        if check_permission(cDriveObject, cDriveUser, cDriveApp, 'V'):
            client = boto3.client(
                's3', 
                region_name = 'us-east-1',
                config=Config(signature_version='s3v4'),
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            url = client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': path
                },
                ExpiresIn=300
            )
            return Response({'download_url' : url}, status=status.HTTP_200_OK)
        else :
            return Response(status=status.HTTP_403_FORBIDDEN)

class ContentView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request):
        cDriveUser, cDriveApp = introspect_token(request)
        
        path = request.query_params['path']
        cDriveObject = get_object_by_path(path)

        if check_permission(cDriveObject, cDriveUser, cDriveApp, 'V'):
            if cDriveObject.__class__.__name__ == 'CDriveFile':
                content = cDriveObject.cdrive_file.read()
                return Response(content, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        else :
            return Response(status=status.HTTP_403_FORBIDDEN)

class JsonContentView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request):
        cDriveUser, cDriveApp = introspect_token(request)
        
        path = request.query_params['path']
        cDriveObject = get_object_by_path(path)

        if check_permission(cDriveObject, cDriveUser, cDriveApp, 'V'):
            if cDriveObject.__class__.__name__ == 'CDriveFile':
                data = []
                csvString = io.StringIO(cDriveObject.cdrive_file.read().decode("utf-8"))
                csvReader = csv.DictReader(csvString)
                for row in csvReader:
                    data.append(row)
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        else :
            return Response(status=status.HTTP_403_FORBIDDEN)

class ShareView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        cDriveUser, cDriveApp = introspect_token(request)

        if cDriveApp.name != 'cdrive':
            return Response(status=status.HTTP_403_FORBIDDEN)

        path = request.data['path']
        target_type = request.data['targetType']
        target_name = request.data['name']
        permission = request.data['permission']
        cDriveObject = get_object_by_path(path)

        if cDriveObject is None:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if target_type == 'application':
            if check_permission(cDriveObject, cDriveUser, cDriveApp, permission):
                target_app = get_app(target_name, cDriveUser)
                if target_app is None:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                share_object(cDriveObject, cDriveUser, target_app, permission)
            else :
                return Response(status=status.HTTP_403_FORBIDDEN)
        elif target_type == 'user':
            if cDriveObject.owner != cDriveUser:
                return Response(status=status.HTTP_403_FORBIDDEN)
            target_user = get_user(target_name)
            if target_user is None: 
                return Response(status=status.HTTP_400_BAD_REQUEST)
            target_app = get_app('cdrive', target_user)
            share_object(cDriveObject, target_user, target_app, permission)

        return Response(status=status.HTTP_200_OK)

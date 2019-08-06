from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from rest_framework.parsers import FileUploadParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import boto3
from botocore.client import Config

from user_mgmt.utils import get_user
from user_mgmt.models import CDriveUser

from .utils import get_object_by_path

class UploadView(APIView):
    parser_class = (FileUploadParser,)

    @csrf_exempt
    def post(self, request):
        cDriveUser = get_user(request)

        if cDriveUser is None:
            return Response(status=status.HTTP_403_FORBIDDEN)

        path = request.data['path']
        parent = get_object_by_path(path)

        queryset = parent.edit_user.objects.filter(username=cDriveUser.name)

        if queryset.exists():
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
        cDriveUser = get_user(request)

        path = request.data['path']

        client = boto3.client(
            's3',
            region_name = 'us-east-1',
            config=Config(signature_version='s3v4'),
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        mpu = client.create_multipart_upload(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=path)

        return Response({'uploadId': mpu['UploadId']}, status=status.HTTP_200_OK)

class UploadChunk(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request):
        cDriveUser = get_user(request)
        path = request.data['path']
        part_number = int(request.data['partNumber'])
        upload_id = request.data['uploadId']
        chunk_data = request.data['chunk']

        client = boto3.client(
            's3',
            region_name = 'us-east-1',
            config=Config(signature_version='s3v4'),
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        part_info = client.upload_part(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=path,
            PartNumber=part_number,
            UploadId=upload_id,
            Body=chunk_data
        )

        etag = part_info['ETag'].strip('\"')

        return Response({'ETag': etag}, status=status.HTTP_200_OK)

class CompleteChunkedUpload(APIView):
    parser_class = (JSONParser,)

    def post(self, request):
        cDriveUser = get_user(request)
        path = request.data['path']
        upload_id = request.data['uploadId']
        parts = request.data['partInfo']
        part_info = { 'Parts': [] }

        parts = parts.split(',')
        for i, part in enumerate(parts, start=1):
            info = { 'ETag': part, 'PartNumber': i }
            part_info['Parts'].append(info)

        size = request.data['size']

        client = boto3.client(
            's3',
            region_name = 'us-east-1',
            config=Config(signature_version='s3v4'),
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        client.complete_multipart_upload(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=path,
            UploadId=upload_id,
            MultipartUpload=part_info
        )

        index = path.rfind('/')
        parent_path = path[0 : index]
        file_name = path[index + 1 : len(path)]
        parent = get_object_by_path(parent_path)
        queryset = parent.edit_user.filter(username=cDriveUser.name)
        if queryset.exists():
            cDriveFile = CDriveFile(
                cdrive_file = path,
                name = file_name,
                owner = cDriveUser,
                parent = parent,
                size = size
            )
            cDriveFile.save()
            return Response(status=status.HTTP_200_OK)
        else :
            return Response(status=status.HTTP_403_FORBIDDEN)

class ListView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request):
        cDriveUser = get_user(request)
        path = request.query_params['path']
        parent = get_object_by_path(path)

        files = CDriveFile.objects.filter(parent=parent)
        files = [f for f in files if f.view_user.objects.filter(username=cDriveUser.name).exists()]
        fileSerializer = CDriveFileSerializer(files, many=True)

        folders = CDriveFolder.objects.filter(parent=parent)
        folders = [f for f in folders if f.view_user.objects.filter(username=cDriveUser.name).exists()]
        folderSerializer = CDriveFolderSerializer(folders, many=True)

        return Response({
            'files' : fileSerializer.data, 
            'folders' :  folderSerializer.data
        }, status=status.HTTP_200_OK)

class DeleteView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def delete(self, request):
        cDriveUser = get_user(request)
        path = request.query_params['path']
        cDriveObject = get_object_by_path(path)
        if cDriveObject.edit_user.objects.filter(username=cDriveUser.name).exists():
            cDriveObject.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else :
            return Response(status=status.HTTP_403_FORBIDDEN)

class DownloadView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def get(self, request):
        cDriveUser = get_user(request)
        path = request.query_params['path']
        cDriveObject = get_object_by_path(path)
        if cDriveObject.view_user.objects.filter(username=cDriveUser.name).exists():
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
                ExpiresIn=3600
            )
            return Response({'download_url' : url}, status=status.HTTP_200_OK)
        else :
            return Response(status=status.HTTP_403_FORBIDDEN)

class ShareView(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        cDriveUser = get_user(request)
        path = request.data['path']
        permission = request.data['permission']
        target_usernames = request.data['target_users']
        cDriveObject = get_object_by_path(path)
        if cDriveObject.share_user.objects.filter(username=cDriveUser.name).exists():
            for username in target_usernames:
                user = CDriveUser.objects.filter(username=username)
                if permission == 'edit':
                    cDriveObject.edit_user.add(user)
                elif permission == 'view':
                    cDriveObject.view_user.add(user)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_200_OK)
        else :
            return Response(status=status.HTTP_403_FORBIDDEN)

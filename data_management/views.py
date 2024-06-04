from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from .models import FileUpload
from .models import UploadedFile
from .forms import FileUploadForm,FileFilterForm 
from django.contrib.auth.decorators import login_required
from django.conf import settings
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError 
from .models import UploadedFile
from django.conf import settings
from azure.storage.blob import BlobServiceClient
from django.http import JsonResponse
from fos_database_server.settings.production import AZURE_STORAGE_CONNECTION_STRING,AZURE_STORAGE_CONTAINER_NAME

@login_required
def file_manage(request):
    form = FileFilterForm(request.GET or None)
    files = FileUpload.objects.all()

    if form.is_valid():
        fos_serial_number = form.cleaned_data.get('fos_serial_number')
        event_type = form.cleaned_data.get('event_type')
        channel = form.cleaned_data.get('channel')
        if fos_serial_number:
            files = files.filter(fos_serial_number__icontains=fos_serial_number)
        if event_type:
            files = files.filter(event_type=event_type)
        if channel:
            files = files.filter(channel=channel)

    context = {'form': form, 'files': files}
    return render(request, 'file_manage.html', context)

def file_manage(request):
    form = FileFilterForm(request.GET or None)
    files = FileUpload.objects.all()

    if form.is_valid():
        if 'use_fos_serial_number' in request.GET and form.cleaned_data['fos_serial_number']:
            files = files.filter(fos_serial_number__icontains=form.cleaned_data['fos_serial_number'])
        if 'use_event_type' in request.GET and form.cleaned_data['event_type']:
            files = files.filter(event_type=form.cleaned_data['event_type'])
        if 'use_channel' in request.GET and form.cleaned_data['channel']:
            files = files.filter(channel=form.cleaned_data['channel'])

    context = {'form': form, 'files': files}
    return render(request, 'file_manage.html', context)


def azure_blob_folders(request):
    settings_file_name = settings.SETTINGS_MODULE.split('.')[-1]
    if settings_file_name == "production":
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(AZURE_STORAGE_CONTAINER_NAME)
        blobs = container_client.list_blobs()
        folders = set()
        for blob in blobs:
            folder_name = blob.name.split('/')[0]
            folders.add(folder_name)
        return JsonResponse(list(folders), safe=False)
    else:
        folders=[]
        return JsonResponse(list(folders), safe=False)

@login_required
def file_upload(request):
    settings_file_name = settings.SETTINGS_MODULE.split('.')[-1]
    form = FileUploadForm(request.POST or None, request.FILES or None) 
    
    if request.method == 'POST':
        if settings_file_name == "production":
            if form.is_valid():
                file = form.cleaned_data['file']
                fos_serial_number = form.cleaned_data['fos_serial_number']
                user_id = request.user.id
                blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
                container_client = blob_service_client.get_container_client(AZURE_STORAGE_CONTAINER_NAME)
                folder_name = fos_serial_number
                blob_client = container_client.get_blob_client(f"{folder_name}/{user_id}/{file.name}")
                try:
                    blob_client.upload_blob(file)
                    uploaded_file = UploadedFile(file_name=file.name, file_url=blob_client.url)
                    uploaded_file.save()
                    new_file = form.save(commit=False)
                    new_file.uploader = request.user
                    new_file.save()
                    messages.success(request, 'File uploaded and verified successfully')
                except ResourceExistsError:
                    messages.success(request, 'File already exists in Azure Blob Storage')
        elif settings_file_name == "development":
            if form.is_valid():
                new_file = form.save(commit=False)
                new_file.uploader = request.user
                new_file.save()
                messages.success(request, 'Files uploaded successfully!')
            else:
                print("Form errors:", form.errors)
                messages.error(request, 'Please correct the errors below.')
    return render(request, 'upload.html', {'form': form})


@login_required
def file_delete(request, file_id):
    settings_file_name = settings.SETTINGS_MODULE.split('.')[-1]
    if request.method == 'POST':
        if settings_file_name == "development":
            file_to_delete=FileUpload.objects.get(pk=file_id)
            file_to_delete.file.delete() 
            file_to_delete.delete()
            return redirect('file-manage')
        
        elif settings_file_name == "production":
            
            file_to_delete = get_object_or_404(FileUpload, pk=file_id)
            user_id = request.user.id
            fos_serial_number = file_to_delete.fos_serial_number
            file_data = str(file_to_delete.file)
            file_name = file_data.split('/')[-1]

            # Azure Blob Storage setup
            connection_string = AZURE_STORAGE_CONNECTION_STRING
            container_name = AZURE_STORAGE_CONTAINER_NAME

            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"{fos_serial_number}/{user_id}/{file_name}")
            blob_client.delete_blob()
            file_to_delete.delete()
            return redirect('file-manage')

        else:
            messages.error(request, "Invalid request")
            return redirect('file-manage')


@login_required
def file_download(request, file_id):
    if request.method == 'POST':
        file_to_download = get_object_or_404(FileUpload, pk=file_id)
        user_id = request.user.id
        fos_serial_number = file_to_download.fos_serial_number
        file_data = str(file_to_download.file)
        file_name = file_data.split('/')[-1]
        connection_string = AZURE_STORAGE_CONNECTION_STRING
        container_name = AZURE_STORAGE_CONTAINER_NAME

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"{fos_serial_number}/{user_id}/{file_name}")
        try:
            blob_data = blob_client.download_blob().readall()
            response = HttpResponse(blob_data, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
        except Exception as e:
            messages.error(request, f"Error downloading file: {e}")
            return redirect('file-manage')

    else:
        messages.error(request, "Invalid request")
        return redirect('file-manage')        

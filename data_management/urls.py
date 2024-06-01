from django.urls import path
from .views import file_upload, file_delete, file_manage, file_analyze, azure_blob_folders

urlpatterns = [
    path('file_upload/', file_upload, name='file-upload'),
    path('file_delete/<int:file_id>/', file_delete, name='file-delete'),
    path('file_manage/', file_manage, name='file-manage'),
    path('analyze/<int:file_id>/', file_analyze, name='file-analyze'),
    path('azure_blob_folders/', azure_blob_folders, name='azure_blob_folders'),
]

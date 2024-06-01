from django.urls import path
from .views import file_upload, file_delete, file_manage, file_analyze

urlpatterns = [
    path('file_upload/', file_upload, name='file-upload'),
    path('file_delete/<int:file_id>/', file_delete, name='file-delete'),
    path('file_manage/', file_manage, name='file-manage'),
    path('analyze/<int:file_id>/', file_analyze, name='file-analyze'),
]

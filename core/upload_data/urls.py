from django.urls import path
from .views import upload_data, data_upload

urlpatterns = [
    path('upload_data/', upload_data, name='upload_data'),
    path('data_upload/', data_upload, name='data_upload'),
]
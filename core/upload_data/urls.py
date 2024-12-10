from django.urls import path
from .views import data_upload_page, upload_student_data

urlpatterns = [
    path('upload_data/', data_upload_page, name='data_upload_page'),
    path('upload_student_data/', upload_student_data, name='upload_student_data'),
]
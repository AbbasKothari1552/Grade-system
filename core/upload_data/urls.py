from django.urls import path
from .views import upload_data,upload_images
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('upload_data/', upload_data, name='upload_data'),
    path('upload_images/',upload_images, name='upload_images'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

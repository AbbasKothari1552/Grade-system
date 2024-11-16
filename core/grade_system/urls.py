from django.urls import path
from .views import basePage, student_grade_view

urlpatterns = [
    path('', basePage, name='basePage'),
    path('grades/<str:enrollment>/', student_grade_view, name='student_grade'),
]
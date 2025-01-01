from django.urls import path
from .views import student, student_grade_view, subject, subject_analysis_view, semester, semester_analysis_view

urlpatterns = [
    path('', basePage, name='basePage'),
    path('grades/<str:enrollment>/', student_grade_view, name='student_grade'),
]
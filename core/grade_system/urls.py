from django.urls import path
from .views import student, student_grade_view, subject, subject_analysis_view, semester, semester_analysis_view

urlpatterns = [
    path('', student, name='student'),
    path('grades/<str:enrollment>/', student_grade_view, name='student_data'),
    path('subject/', subject, name='subject'),
    path('subject/<str:subject>/<str:year>/<str:type>', subject_analysis_view, name='subject_data'),
    path('semester/', semester, name='semester'),
    path('semester/<str:semester>/<str:year>/<str:type>', semester_analysis_view, name='semester_data'),
]
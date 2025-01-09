from django.urls import path
from .views import student, student_grade_view, subject, subject_analysis_view, semester, semester_analysis_view, student_name_suggestions

urlpatterns = [
    path('', student, name='student'),
<<<<<<< HEAD
    path('name-suggestions/', student_name_suggestions, name="name-suggestions"), 
    path('student_grades/', student_grade_view, name='student_data'),
=======
    path('grades/<str:enrollment>/', student_grade_view, name='student_data'),
>>>>>>> 85bc40b751fc80ec053d8a30f944f1914edbcb2b
    path('subject/', subject, name='subject'),
    path('subject/<str:subject>/<str:year>/<str:type>', subject_analysis_view, name='subject_data'),
    path('semester/', semester, name='semester'),
    path('semester/<str:semester>/<str:year>/<str:type>', semester_analysis_view, name='semester_data'),
]
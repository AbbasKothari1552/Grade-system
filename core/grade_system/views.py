from django.shortcuts import render, get_object_or_404
from .models import Branch, Subject, ExamData, BranchSubjectSemester, StudentInfo, StudentExam, GradeData, Result


def basePage(request):
    return render(request, 'login.html')


def student_grade_view(request, enrollment):
    
    # get student information
    student = get_object_or_404(StudentInfo, enrollment=enrollment)

    # Get all the exams for the student
    student_exams = StudentExam.objects.filter(student_info=student).order_by('exam_data__semester')

    # Collect grade data and results for each exam
    exam_data = []
    for student_exam in student_exams:
        # Get grade data for each subject in this exam
        grades = GradeData.objects.filter(student_exam=student_exam)

        # Get the result for this exam
        result = Result.objects.filter(student_exam=student_exam).first()

        # Collect semester-wise data
        exam_data.append({
            'exam': student_exam.exam_data,
            'grades': grades,
            'sgpa': result.sgpa if result else None,
            'cgpa': result.cgpa if result else None,
            'backlog': result.backlog if result else None,
            'result': result.result if result else None,
        })
    
    # Pass all the collected data to the template
    context = {
        'student': student,
        'exam_data': exam_data,
    }

    return render(request, 'index.html', context)

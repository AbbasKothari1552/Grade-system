from django.db.models import Max
from django.shortcuts import render, get_object_or_404
from .models import Branch, Subject, ExamData, BranchSubjectSemester, StudentInfo, StudentExam, GradeData, Result


def basePage(request):
    return render(request, 'login.html')


def student_grade_view(request, enrollment):
    
    # get student information
    student = get_object_or_404(StudentInfo, enrollment=enrollment)

    # Get all the exams for the student
    student_exams = StudentExam.objects.filter(student_info=student).order_by('exam_data__semester')

    # Get the largest semester value
    current_semester = student_exams.aggregate(Max('exam_data__semester'))['exam_data__semester__max']
    current_semester = int(current_semester[-1])
    if current_semester != 8:
        current_semester += 1

    # Collect grade data and results for each exam
    exam_data = []
    for student_exam in student_exams:

        if student_exam.exam_data.exam_type == "REPETER":
            main_exam = StudentExam.objects.filter(
                student_info=student_exam.student_info, 
                exam_data__semester=student_exam.exam_data.semester, 
                exam_data__exam_type="REGULAR").first()
            
            if main_exam:
                failed_subjects = GradeData.objects.filter(student_exam=main_exam, grade="FF")

                # Get the backlog subjects for the repeater exam
                grades = GradeData.objects.filter(
                    student_exam=student_exam,
                    subject_bss__in=failed_subjects.values_list('subject_bss', flat=True)  # Match only failed subjects
                )
            else:
                print("Main exam not found.")
        else:
            # Get grade data for each subject in this exam
            grades = GradeData.objects.filter(student_exam=student_exam)

        # # Filter grades to include only subjects where grade is 'FF'
        # failed_grades = grades.filter(grade='FF')

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
        'current_semester' : current_semester,
    }

    return render(request, 'index.html', context)

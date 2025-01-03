from django.db.models import Max, Count
from django.db.models import Max, Count
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.http import Http404
from django.contrib import messages
from django.http import Http404
from .models import Branch, Subject, ExamData, BranchSubjectSemester, StudentInfo, StudentExam, GradeData, Result
import json
import json

# Base Page Student enrollement Entry.
def student(request):
    return render(request, 'student.html')
# Base Page Student enrollement Entry.
def student(request):
    return render(request, 'student.html')

# Student grade history view.
# Student grade history view.
def student_grade_view(request, enrollment):

    try:
        # get student information
        student = get_object_or_404(StudentInfo, enrollment=enrollment)

        # Get all the exams for the student
        student_exams = StudentExam.objects.filter(student_info=student).order_by('exam_data__semester')
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
            # Check exam type
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

        # Backlog summary for 8 semester.
        backlog_summary = []
        for semester in range(1,9):
            semester_data = next(
            (data for data in exam_data if data['exam'].semester == f"SEMESTER {semester}" and data['exam'].exam_type == "REGULAR"),
            None
            )
            backlog_summary.append({
                'semester': semester,
                'backlog': semester_data['backlog'] if semester_data else '-'  # Show backlog count or dash
            })
        
        # Pass all the collected data to the template
        context = {
            'student': student,
            'exam_data': exam_data,
            'backlog_summary': backlog_summary, 
            'current_semester': current_semester,
        }

        return render(request, 'student_data.html', context)
    except Http404:
        # If student is not found, display a message
        messages.error(request, "Incorrect enrollment number. Please try again.")
        return render(request, 'student.html')


# Subject wise search template render view.
def subject(request):
    branch = "BACHELOR OF TECHNOLOGY (COMPUTER SCIENCE AND DESIGN)"
    subjects = BranchSubjectSemester.objects.filter(branch__branch_name=branch).values_list('subject__subject_name', flat=True)
    # Get distinct academic_year values
    academic_years = ExamData.objects.values_list('academic_year', flat=True).distinct()
    context = {
        'subjects' : subjects,
        'academic_years' : academic_years,
    }
    return render(request, "subject.html", context)

# Subject wise student Data Display.
def subject_analysis_view(request, subject, year, type):
    
    branch = "BACHELOR OF TECHNOLOGY (COMPUTER SCIENCE AND DESIGN)"
    students_grade = GradeData.objects.filter(
                                            student_exam__student_info__branch__branch_name=branch,
                                            subject_bss__subject__subject_name=subject,
                                            student_exam__exam_data__academic_year=year,
                                            student_exam__exam_data__exam_type=type,
                                            ).select_related(
                                            'student_exam__student_info__branch',
                                            'student_exam__exam_data',
                                            'subject_bss__subject',
                                            ).order_by('student_exam__student_info__enrollment')
    # Grade counting
    grade_counts_data = students_grade.values("grade").annotate(count=Count("grade")).order_by("grade")
    # Convert queryset to JSON-compatible format
    grade_counts_json = json.dumps(list(grade_counts_data))

    # Prepare data for the chart
    grade_labels = [entry['grade'] for entry in grade_counts_data]
    grade_counts = [entry['count'] for entry in grade_counts_data]

    context = {
        'students_grade' : students_grade,
        'grade_counts_data' : grade_counts_data,
        'grade_labels' : grade_labels,
        'grade_counts' : grade_counts
    }
    return render(request, 'subject_data.html', context)


# Semester wise search template render view.
def semester(request):
    # Get distinct academic_year values
    academic_years = ExamData.objects.values_list('academic_year', flat=True).distinct()
    context = {
        'academic_years' : academic_years,
    }
    return render(request, "semester.html", context)

def semester_analysis_view(request, semester, year, type):
    branch = "BACHELOR OF TECHNOLOGY (COMPUTER SCIENCE AND DESIGN)"
    
    # Concatenating to match the database value
    semester = "SEMESTER " + semester

    # Get all subjects for the given branch and semester
    subjects = BranchSubjectSemester.objects.filter(
        branch__branch_name=branch,
        semester=semester
    ).values_list('subject__subject_name', flat=True)

    # Get all students and their grades for the given branch, semester, and academic year
    students_grade = GradeData.objects.filter(
        student_exam__student_info__branch__branch_name=branch,
        student_exam__exam_data__academic_year=year,
        student_exam__exam_data__semester=semester,
        student_exam__exam_data__exam_type=type,
    ).select_related(
        'student_exam__student_info',
        'student_exam__exam_data'
        ).order_by('student_exam__student_info__enrollment')

    # Organize data for the template
    table_data = []
    for student in students_grade:
        # Check if the student is already in the table data
        enrollment = student.student_exam.student_info.enrollment
        name = student.student_exam.student_info.name
        subject_name = student.subject_bss.subject.subject_name
        grade = student.grade

        # Find or create the row for the student
        row = next((r for r in table_data if r['enrollment'] == enrollment), None)
        if not row:
            row = {
                'enrollment': enrollment,
                'name': name,
                'grades': {sub: "-" for sub in subjects}  # Initialize with dashes for all subjects
            }
            table_data.append(row)
        
        # Add the grade for the specific subject
        row['grades'][subject_name] = grade

    context = {
        'subjects': subjects,  # List of subjects
        'table_data': table_data,  # Student and grades data
        'semester': semester,
        'academic_year': year,
        'exam': students_grade[0].student_exam.exam_data.exam_name if students_grade.exists() else None,
        'declaration_date': students_grade[0].student_exam.exam_data.declaration_date if students_grade.exists() else None,
        'exam_type': type,
    }

    return render(request, "semester_data.html", context)

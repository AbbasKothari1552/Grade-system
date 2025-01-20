from django.shortcuts import render, get_object_or_404
from django.db.models import Max, Count
from django.contrib import messages
from django.http import Http404, JsonResponse
from .models import ExamData, StudentInfo, StudentExam, GradeData, Result, Subject, Branch, CollegeName
import json

# Base Page Student enrollement Entry.
def student(request):
    return render(request, 'student.html')

# Name suggestion of student 
def student_name_suggestions(request):
    """
    This view handles the Suggestion of names on the 
    student.html page while user search for student's
    grade history by Name.
    """
    if 'query' in request.GET:
        query = request.GET['query']
        # Filter students whose name contains the query (case-insensitive)
        students = StudentInfo.objects.filter(name__icontains=query).values_list('name', flat=True)
        return JsonResponse({'suggestions': list(students)}, safe=False)
    return JsonResponse({'suggestions': []})

# Student grade history view
def student_grade_view(request):

    if request.method == "GET":
        try:
            enrollment = request.GET.get('enrollment')
            name = request.GET.get('name')
            if enrollment:
                # Search by enrollment number
                student = get_object_or_404(StudentInfo, enrollment=enrollment)
            elif name:
                # Search by name
                student = get_object_or_404(StudentInfo, name__icontains=name)
            else:
                # No search criteria provided
                messages.error(request, "Please provide either an enrollment number or a name to search.")
                return render(request, 'student.html')

            # Get all the exams for the student
            student_exams = StudentExam.objects.filter(student_info=student).order_by('exam_data__semester')

            # Get the largest semester value
            current_semester = student_exams.aggregate(Max('exam_data__semester'))['exam_data__semester__max']
            if current_semester:
                current_semester = int(current_semester[-1])
                if current_semester != 8:
                    current_semester += 1
            else:
                current_semester = 1

            # Collect grade data and results for each exam
            exam_data = []
            for student_exam in student_exams:
                if student_exam.exam_data.exam_type == "REPETER":
                    main_exam = StudentExam.objects.filter(
                        student_info=student_exam.student_info,
                        exam_data__semester=student_exam.exam_data.semester,
                        exam_data__exam_type="REGULAR"
                    ).first()

                    if main_exam:
                        failed_subjects = GradeData.objects.filter(student_exam=main_exam, grade__in=["FF", "FF*", "nan"])
                        grades = GradeData.objects.filter(
                            student_exam=student_exam,
                            subject__in=failed_subjects.values_list('subject', flat=True)
                        )
                    else:
                        grades = []
                else:
                    grades = GradeData.objects.filter(student_exam=student_exam)

                result = Result.objects.filter(student_exam=student_exam).first()

                exam_data.append({
                    'exam': student_exam.exam_data,
                    'grades': grades,
                    'sgpa': result.sgpa if result else None,
                    'cgpa': result.cgpa if result else None,
                    'backlog': result.backlog if result else None,
                    'result': result.result if result else None,
                })

            # Backlog summary for 8 semesters
            backlog_summary = []
            for semester in range(1, 9):
                semester_data = next(
                    (data for data in exam_data if data['exam'].semester == f"SEMESTER {semester}" and data['exam'].exam_type == "REGULAR"),
                    None
                )
                backlog_summary.append({
                    'semester': semester,
                    'backlog': semester_data['backlog'] if semester_data else '-'
                })

            admission_year = student.admission_year

            context = {
                'student': student,
                'exam_data': exam_data,
                'backlog_summary': backlog_summary,
                'current_semester': current_semester,
                'admission_year': admission_year,
            }

            return render(request, 'student_data.html', context)

        except Http404:
            messages.error(request, "Student not found. Please check the details and try again.")
            return render(request, 'student.html')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, 'student.html')
    else:
        return render(request, 'student.html')

# Subject wise search template render view.
def subject(request):
    subjects = Subject.objects.values_list('subject_name', flat=True)
    # Get distinct academic_year values
    academic_years = ExamData.objects.values_list('academic_year', flat=True).distinct()
    branches = Branch.objects.values_list('branch_name', flat=True)
    colleges = CollegeName.objects.values_list('college_name', flat=True)
    context = {
        'subjects' : subjects,
        'academic_years' : academic_years,
        'branches': branches,
        'colleges':colleges,
    }
    return render(request, "subject.html", context)

# Subject wise student Data Display.
def subject_analysis_view(request, subject, year, branch, college, type):
    
    # branch = "BACHELOR OF TECHNOLOGY (COMPUTER SCIENCE AND DESIGN)"
    students_grade = GradeData.objects.filter(
                                            subject__subject_name=subject,
                                            student_exam__exam_data__academic_year=year,
                                            student_exam__student_info__branch__branch_name=branch,
                                            student_exam__student_info__college__college_name=college,
                                            student_exam__exam_data__exam_type=type,
                                            ).select_related(
                                            'student_exam__student_info__branch',
                                            'student_exam__exam_data',
                                            ).order_by('student_exam__student_info__enrollment')
    # Grade counting
    grade_counts_data = students_grade.values("grade").annotate(count=Count("grade")).order_by("grade")

    # Prepare data for the chart
    grade_labels = [entry['grade'] for entry in grade_counts_data]
    grade_counts = [entry['count'] for entry in grade_counts_data]

    context = {
        'students_grade' : students_grade,
        'students_grade_exists': students_grade.exists(),
        'grade_counts_data' : grade_counts_data,
        'grade_labels' : grade_labels,
        'grade_counts' : grade_counts
    }
    return render(request, 'subject_data.html', context)


# Semester wise search template render view.
def semester(request):
    # Get distinct academic_year values
    academic_years = ExamData.objects.values_list('academic_year', flat=True).distinct()
    branches = Branch.objects.values_list('branch_name', flat=True)
    colleges = CollegeName.objects.values_list('college_name', flat=True)
    context = {
        'academic_years' : academic_years,
        'branches': branches,
        'colleges':colleges,
    }
    return render(request, "semester.html", context)

# Semester-wise analysis view
def semester_analysis_view(request, semester, year, branch, college, type):

    # Format semester to match database value
    semester = "SEMESTER " + semester

    # Fetch the first matching ExamData object
    exam_data = ExamData.objects.filter(
        semester=semester,
        academic_year=year,
        branch__branch_name=branch,
        college__college_name=college,
        exam_type=type,
    ).first()

    # Handle case where no matching exam data exists
    if not exam_data:
        return render(request, "semester_data.html", {"error": "No data found for the selected semester."})

    # Extract exam name and declaration date
    exam_name = exam_data.exam_name
    declaration_date = exam_data.declaration_date

    # Fetch all StudentExam objects for the given exam data
    student_exams = StudentExam.objects.filter(exam_data=exam_data).order_by('student_info__enrollment')

    # Fetch GradeData and all unique subjects for the given student exams
    grade_data = GradeData.objects.filter(student_exam__in=student_exams).select_related('subject', 'student_exam')
    subjects = Subject.objects.filter(gradedata__student_exam__in=student_exams).distinct()
    subject_names = list(subjects.values_list('subject_name', flat=True))  # List of all subject names
    subject_ids = list(subjects.values_list('id', flat=True))  # List of subject IDs for mapping grades

    # Prepare data for student grades
    student_grades = []
    for student_exam in student_exams:
        student = student_exam.student_info  # Assuming StudentExam has a ForeignKey to Student

        # Initialize grades dictionary with "-" for all subjects
        grades = {subject_id: "-" for subject_id in subject_ids}

        # Map grades for the student
        for grade in grade_data.filter(student_exam=student_exam):
            grades[grade.subject.id] = grade.grade  # Assign grade for the specific subject

        # Append student data with grades to the list
        student_grades.append({
            'enrollment': student.enrollment,  
            'student_name': student.name, 
            'grades': [grades[subject_id] for subject_id in subject_ids],  # Map grades in subject order
        })

    # Context for rendering the template
    context = {
        'semester': semester,
        'year': year,
        'exam_name': exam_name,
        'declaration_date': declaration_date,
        'type': type,
        'subjects': subject_names,  # Subject names to display in table headers
        'student_grades': student_grades,  # Student grades to display in rows
    }


    return render(request, "semester_data.html", context)

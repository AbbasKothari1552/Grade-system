from django.shortcuts import render, get_object_or_404
from django.db.models import Max, Count
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.contrib import messages
from .models import ExamData, BranchSubjectSemester, StudentInfo, StudentExam, GradeData, Result
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

            print(name)

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
                        failed_subjects = GradeData.objects.filter(student_exam=main_exam, grade="FF")
                        grades = GradeData.objects.filter(
                            student_exam=student_exam,
                            subject_bss__in=failed_subjects.values_list('subject_bss', flat=True)
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
            
            

            context = {
                'student': student,
                'exam_data': exam_data,
                'backlog_summary': backlog_summary,
                'current_semester': current_semester,
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
    context = {
        'academic_years' : academic_years,
    }
    return render(request, "semester.html", context)


# Semester wise analysis view.
def semester_analysis_view(request, semester, year, type):
    branch = "BACHELOR OF TECHNOLOGY (COMPUTER SCIENCE AND DESIGN)"
    
    # Concatenate to match the database value
    semester = "SEMESTER " + semester

    # Get all subjects for the given branch and semester
    all_subjects = BranchSubjectSemester.objects.filter(
        branch__branch_name=branch,
        semester=semester
    ).select_related('subject')

    # Categorize subjects into core and elective subjects
    core_subjects = all_subjects.filter(is_core=True)
    professional_electives = all_subjects.filter(elective_group="PROFESSIONAL")
    open_electives = all_subjects.filter(elective_group="OPEN")

    # Get all grades for students in the given semester, academic year, and exam type
    students_grade = GradeData.objects.filter(
        student_exam__student_info__branch__branch_name=branch,
        student_exam__exam_data__academic_year=year,
        student_exam__exam_data__semester=semester,
        student_exam__exam_data__exam_type=type,
    ).select_related(
        'student_exam__student_info',
        'student_exam__exam_data',
        'subject_bss__subject'
    ).order_by('student_exam__student_info__enrollment')

    # Map student grades for faster access
    student_grades = {}
    for grade in students_grade:
        enrollment = grade.student_exam.student_info.enrollment
        subject_id = grade.subject_bss.subject.id
        if enrollment not in student_grades:
            student_grades[enrollment] = {
                'name': grade.student_exam.student_info.name,
                'grades': {},
                'electives': {'professional': [], 'open': []}
            }
        if grade.subject_bss.is_core:
            student_grades[enrollment]['grades'][subject_id] = grade.grade
        elif grade.subject_bss.elective_group == "PROFESSIONAL":
            student_grades[enrollment]['electives']['professional'].append({
                'subject_name': grade.subject_bss.subject.subject_name,
                'grade': grade.grade
            })
        elif grade.subject_bss.elective_group == "OPEN":
            student_grades[enrollment]['electives']['open'].append({
                'subject_name': grade.subject_bss.subject.subject_name,
                'grade': grade.grade
            })

    # Create table_data for core subjects (Table 1)
    core_subject_order = [subject.subject.id for subject in core_subjects]
    core_headers = ["Enrollment", "Name"] + [subject.subject.subject_name for subject in core_subjects]
    core_table_data = []

    for enrollment, data in student_grades.items():
        row = [enrollment, data['name']]  # Enrollment and name
        for subject_id in core_subject_order:
            grade = data['grades'].get(subject_id, "-")  # Get grade or "-"
            row.append(grade)
        core_table_data.append(row)

    # Create table_data for elective subjects (Table 2)
    elective_table_data = []
    for enrollment, data in student_grades.items():
        if data['electives']['professional'] or data['electives']['open']:
            for i in range(max(len(data['electives']['professional']), len(data['electives']['open']))):
                professional = data['electives']['professional'][i] if i < len(data['electives']['professional']) else {'subject_name': "-", 'grade': "-"}
                open_elective = data['electives']['open'][i] if i < len(data['electives']['open']) else {'subject_name': "-", 'grade': "-"}
                elective_table_data.append([
                    professional['subject_name'], professional['grade'],
                    open_elective['subject_name'], open_elective['grade']
                ])
    
    combined_data = []
    if elective_table_data:
        for core_row, elective_row in zip(core_table_data, elective_table_data):
            combined_data.append({
                'core': core_row,  # A list containing enrollment, name, and core grades
                'elective': elective_row  # A list containing professional and open electives
            })
    

    # Pass data to the template
    context = {
        'core_headers': core_headers,
        'core_table_data': core_table_data,
        'combined_data': combined_data,
        # 'elective_table_data': elective_table_data,
        'semester': semester,
        'academic_year': year,
        'exam': students_grade[0].student_exam.exam_data.exam_name if students_grade.exists() else None,
        'declaration_date': students_grade[0].student_exam.exam_data.declaration_date if students_grade.exists() else None,
        'exam_type': type,
    }


    return render(request, "semester_data.html", context)

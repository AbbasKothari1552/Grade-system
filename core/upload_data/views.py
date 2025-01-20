import pandas as pd
from django.core.exceptions import *
from django.db import transaction
from django.db.utils import IntegrityError
from django.shortcuts import render, redirect
from django.contrib import messages
from grade_system.models import StudentInfo, ExamData, StudentExam, Subject, GradeData, Result, Branch, CollegeName


def load_file(file):
    """
    Load an uploaded Excel or CSV file into a Pandas DataFrame.

    Parameters:
        file (InMemoryUploadedFile): The uploaded file object (from Django request.FILES).

    Returns:
        pd.DataFrame: Pandas DataFrame containing the file data.

    Raises:
        ValueError: If the file format is unsupported or an error occurs while reading.
    """
    try:
        # Check the content type or file name for file format
        if file.name.endswith('.xlsx'):
            # For modern Excel files (.xlsx), use openpyxl
            df = pd.read_excel(file, engine='openpyxl')
        elif file.name.endswith('.xls'):
            # For older Excel files (.xls), use xlrd
            df = pd.read_excel(file, engine='xlrd')
        elif file.name.endswith('.csv'):
            # For CSV files, use pandas.read_csv
            df = pd.read_csv(file)
        else:
            raise ValueError("Unsupported file format. Please upload .xlsx, .xls, or .csv files.")
        
        print("File loaded successfully.")
        return df

    except Exception as e:
        raise ValueError(f"Error processing file: {e}")



def process_excel_file(request, file):

    try:
        # Step 1: Parse Excel file
        data = load_file(file)

        with transaction.atomic():
            
            for _, row in data.iterrows():
                # Extract Student Info
                spid = row['SPDID']
                enrollment = row['EnrolmentNumber']
                name = row['StudentName']
                gender = row['GenderName']
                dob = row['BirthDate']
                faculty_name = row['FacultyName']
                college_code = row['CollegeCode']
                college_name = row['CollegeName']
                program_code = row['ProgramCode']
                program_name = row['ProgrammeName']
                semester = row['ProgramTermName']
                exam_name = row['ExamName']
                exam_month = row['ExamMonth']
                exam_year = row['ExamYear']
                exam_type = row['ExamType']
                declaration_date = row['DeclarationDate']
                academic_year = row['AcadamicYear']
                seat_no = row['ExamSeatNo']
                sgpa = row['SGPA']
                cgpa = row['CGPA']
                backlog = row['CurrentSemBacklog']
                result_status = row['RESULT']
                ufm = row['UFM']

                college, created_college = CollegeName.objects.get_or_create(
                    college_code = college_code,
                    college_name = college_name
                )

                branch, created_branch = Branch.objects.get_or_create(
                    branch_code = program_code,
                    branch_name = program_name
                )

                # Step 2: Add or Get StudentInfo
                student, created_student = StudentInfo.objects.get_or_create(
                    spid=spid,
                    defaults={
                        'enrollment': enrollment,
                        'name': name,
                        'gender': gender,
                        'date_of_birth': dob,
                        'faculty_name': faculty_name,
                        'college': college,
                        'branch': branch,
                        'admission_year':"20"+str(enrollment)[1]+str(enrollment)[2],
                    }
                )

                # Step 3: Add or Get ExamData
                exam, created_exam = ExamData.objects.get_or_create(
                    exam_name=exam_name,
                    semester=semester,
                    branch=branch,
                    college=college,
                    defaults={
                        'exam_month': exam_month,
                        'exam_year': exam_year,
                        'exam_type': exam_type,
                        'declaration_date': declaration_date,
                        'academic_year': academic_year,
                        'admission_year':"20"+str(enrollment)[1]+str(enrollment)[2],
                    }
                )

                # Step 4: Add or Get StudentExam
                student_exam, created_student_exam = StudentExam.objects.get_or_create(
                    student_info=student,
                    exam_data=exam,
                    defaults={'seat_no': seat_no}
                )

                # Step 5: Validate Subjects and Add Grades
                for i in range(1, 12):  # Loop through all subjects (SUB1 to SUB11)
                    subject_code = row.get(f'SUB{i}PaperCode')
                    subject_name = row.get(f'SUB{i}Name')
                    credits = row.get(f'SUB{i}Credits')
                    grade = row.get(f'SUB{i}OverallGrade1')

                    if pd.isna(subject_code) or pd.isna(subject_name):
                        # Skip if the subject is not provided
                        continue

                    subject, created_subject = Subject.objects.get_or_create(
                        subject_code = subject_code,
                        subject_name = subject_name,
                    defaults={
                        'credits': credits,
                    }
                    )

                    # Add GradeData
                    GradeData.objects.create(
                        student_exam=student_exam,
                        subject=subject,
                        grade=grade,
                    )
    
                # Step 6: Add Result
                Result.objects.get_or_create(
                    student_exam=student_exam,
                    defaults={
                        'sgpa': sgpa,
                        'cgpa': cgpa,
                        'backlog': backlog,
                        'ufm': True if str(ufm).strip().lower() == "yes" else False,
                        'result': result_status
                    }
                )

        print("All data successfully processed and saved.")
        messages.success(request, "All data successfully processed and saved.")

    except IntegrityError as e:
        print(f"Transaction failed: {e}")
        messages.error(request, e)
    except Exception as e:
        print(f"Error processing file: {e}")
        messages.error(request, e)


def upload_data(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        process_excel_file(request, file)
        return redirect("upload_data")
    
    # pass exam names with college name
    exam_data = ExamData.objects.all()
    # get all colleges name
    colleges = CollegeName.objects.all()

    context = {
        'exam_data': exam_data,
        'colleges': colleges
    }

    return render(request, "upload_data.html", context)


def upload_images(request):
    if request.method == "POST":
        images = request.FILES.getlist('images')  # Get all uploaded files
        errors = []
        students = []
        
        # Step 1: Validate all images
        for image in images:
            image_name = (image.name).split(".")
            try:
                enrollment_number = int(image_name[0])  # Extract enrollment number
                student = StudentInfo.objects.get(enrollment=enrollment_number)
                students.append((student, image))  # Store valid students and images in a list
            except (ValueError, IndexError):
                errors.append(f"Invalid file name format: {image.name}")
            except StudentInfo.DoesNotExist:
                errors.append(f"No student found with enrollment number: {image_name[0]}")

        # Step 2: If there are errors, redirect with error messages
        if errors:
            for error in errors:
                messages.error(request, error)  # Add each error message to Django messages
            return redirect('upload_data')  # Replace 'upload_template' with the name of your template

        # Step 3: Save all valid images
        for student, image in students:
            student.image.save(image.name, image)  # Save each image to the respective student's image field
        
        messages.success(request, "All images were successfully uploaded.")
        return redirect('upload_data')  # Redirect to the same or another template after successful upload

    messages.error(request, "Invalid request method.")
    return redirect('upload_data')  # Redirect for non-POST requests


def delete_data(request):
    if request.method=="POST":
        exam_name=request.POST.get("exam_name")
        college_name=request.POST.get("college_name")
        print(exam_name, college_name)
        exam=ExamData.objects.filter(exam_name=exam_name, college__college_name=college_name)
        exam.delete()
        print("data Deleted")
        messages.success(request,"Data Deleted")
        return redirect("upload_data")
    return redirect("upload_data")


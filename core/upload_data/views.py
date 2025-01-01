import pandas as pd
from django.db import transaction
from django.db.utils import IntegrityError
from django.shortcuts import render, redirect
from datetime import datetime
from grade_system.models import StudentInfo, ExamData, StudentExam, BranchSubjectSemester, Subject, GradeData, Result, Branch


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



def process_excel_file(file):

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

                # Step 2: Add or Get StudentInfo
                student, created_student = StudentInfo.objects.get_or_create(
                    spid=spid,
                    defaults={
                        'enrollment': enrollment,
                        'name': name,
                        'gender': gender,
                        'date_of_birth': dob,
                        'faculty_name': faculty_name,
                        'college_code': college_code,
                        'college_name': college_name,
                        'branch': Branch.objects.get(branch_code=program_code),
                    }
                )

                # Step 3: Add or Get ExamData
                exam, created_exam = ExamData.objects.get_or_create(
                    exam_name=exam_name,
                    exam_month=exam_month,
                    exam_year=exam_year,
                    exam_type=exam_type,
                    semester=semester,
                    declaration_date=declaration_date, # **on hold for now, ask sir**
                    academic_year=academic_year
                )

                # Step 4: Add or Get StudentExam
                student_exam, created_student_exam = StudentExam.objects.get_or_create(
                    student_info=student,
                    exam_data=exam,
                    defaults={'seat_no': seat_no}
                )

                # Step 5: Validate Subjects and Add Grades
                for i in range(1, 12):  # Loop through all subjects (SUB1 to SUB11)
                    paper_code = row.get(f'SUB{i}PaperCode')
                    subject_name = row.get(f'SUB{i}Name')
                    credits = row.get(f'SUB{i}Credits')
                    grade = row.get(f'SUB{i}OverallGrade1')

                    if pd.isna(paper_code) or pd.isna(subject_name):
                        # Skip if the subject is not provided
                        continue

                    # Check if the subject exists in the BranchSubjectSemester model
                    subject = Subject.objects.filter(subject_code=paper_code).first()
                    if not subject:
                        raise IntegrityError(f"Subject with code {paper_code} is missing from the database.")

                    branch_subject = BranchSubjectSemester.objects.filter(
                        subject=subject,
                        branch_id=student.branch_id,
                        semester=semester
                    ).first()

                    if not branch_subject:
                        raise IntegrityError(f"Subject {paper_code} ({subject_name}) is not configured for branch {program_code} and semester {semester}.")

                    # Add GradeData
                    GradeData.objects.get_or_create(
                        student_exam=student_exam,
                        subject_bss=branch_subject,
                        defaults={'grade': grade}
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

    except IntegrityError as e:
        print(f"Transaction failed: {e}")
    except Exception as e:
        print(f"Error processing file: {e}")


def upload_data(request):

    if request.method == 'POST':
        file = request.FILES.get('file')
        process_excel_file(file)
        return redirect("upload_data")
    
    return render(request, "upload_data.html")

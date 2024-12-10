import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from openpyxl import load_workbook
from grade_system.models import StudentInfo, Branch


def data_upload_page(request):
    return render(request, 'upload_student_data.html')


def upload_student_data(request):
    """
    ->This view take excel file as input for new student data entry in database.
    ->The function checks for the required column in file.
    ->The function checks for the duplicate or already exists entry &
      also missing values.
    """
    errors = []  # To store all error messages
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            errors.append("No file uploaded.")
            return render(request, 'upload_student_data.html', {'errors': errors})

        try:
            # Read the Excel file
            df = pd.read_excel(uploaded_file)
            print(df.columns)

            # Define required columns
            required_columns = [
                'spid', 'enrollment', 'name', 'gender', 
                'date_of_birth', 'faculty_name', 
                'college_code', 'college_name', 'branch'
            ]

            # Check for missing columns
            for col in required_columns:
                if col not in df.columns:
                    errors.append(f"Missing required column: {col}")

            # If required columns are missing, stop processing
            if errors:
                return render(request, 'upload_student_data.html', {'errors': errors})

            # Validate rows for missing values and conflicts
            for index, row in df.iterrows():
                missing_fields = [col for col in required_columns if pd.isnull(row[col])]
                if missing_fields:
                    errors.append(f"Row {index + 1}: Missing values in columns {missing_fields}")

                # Check for duplicate SPID and Enrollment in database
                if not pd.isnull(row['spid']) and StudentInfo.objects.filter(spid=row['spid']).exists():
                    errors.append(f"Row {index + 1}: SPID '{row['spid']}' already exists.")

                if not pd.isnull(row['enrollment']) and StudentInfo.objects.filter(enrollment=row['enrollment']).exists():
                    errors.append(f"Row {index + 1}: Enrollment '{row['enrollment']}' already exists.")

                # Check if branch exists in the database
                if not pd.isnull(row['branch']) and not Branch.objects.filter(branch_name=row['branch']).exists():
                    errors.append(f"Row {index + 1}: Branch '{row['branch']}' does not exist in the database.")

            # If errors are found, stop processing
            if errors:
                return render(request, 'upload_student_data.html', {'errors': errors})

            # If no errors, create entries in the database
            for index, row in df.iterrows():
                branch_instance = Branch.objects.get(branch_name=row['branch'])  # Fetch branch instance
                StudentInfo.objects.create(
                    spid=row['spid'],
                    enrollment=row['enrollment'],
                    name=row['name'],
                    gender=row['gender'],
                    date_of_birth=row['date_of_birth'],
                    faculty_name=row['faculty_name'],
                    college_code=row['college_code'],
                    college_name=row['college_name'],
                    branch=branch_instance
                )

            return JsonResponse({'message': 'All entries successfully added to the database.'})

        except Exception as e:
            print(e)
            errors.append(f"Error processing the file: {str(e)}")
    
    return render(request, 'upload_student_data.html', {'errors': errors})


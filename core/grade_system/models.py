from django.db import models

# Create your models here.


# Branch Model
class Branch(models.Model):
    id = models.AutoField(primary_key=True)
    branch_code = models.IntegerField(unique=True)
    branch_name = models.CharField(max_length=100)

    def __str__(self):
        return self.branch_name


# Subject Model
class Subject(models.Model):
    id = models.AutoField(primary_key=True)
    subject_code = models.IntegerField(unique=True)
    subject_name = models.CharField(max_length=100, unique=True)
    credits = models.IntegerField()

    def __str__(self):
        return self.subject_name

#ExamData Model
class ExamData(models.Model):
    types=[
        ("Regular","Regular"),
        ("Repeater","Repeater"),
      
             ]
    id = models.AutoField(primary_key=True)
    exam_name = models.CharField(max_length=100)
    exam_month = models.CharField(max_length=10)
    exam_year = models.IntegerField()
    exam_type = models.CharField(max_length=8,choices=types)
    semester = models.IntegerField()
    declaration_date = models.DateField()
    academic_year = models.CharField(max_length=9)

    def __str__(self):
        return self.exam_name

# Branch-Subject-Semester Model
class BranchSubjectSemester(models.Model):
    type=[
        ("Professional","Professional"),
        ("Elective","Elective"),
    ]
    id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    semester = models.IntegerField()
    is_core = models.BooleanField()
    elective_group = models.CharField(max_length=50, blank=True, null=True,choices=type)

    class Meta:
        unique_together = ('subject', 'branch', 'semester')

    def __str__(self):
        return f"{self.branch.branch_name} - {self.subject.subject_name} - Sem {self.semester}"

# Student Info Model
class StudentInfo(models.Model):
    gender_type=[
        ("Male","Male"),
        ("Female","Female")
    ]
    id = models.AutoField(primary_key=True)
    spid = models.CharField(unique=True,max_length=10)
    enrollment = models.CharField(unique=True,max_length=14)
    name = models.CharField(max_length=100)
    gender = models.CharField(choices=gender_type,max_length=6)  # True for male, False for female (or consider using CharField with choices)
    date_of_birth = models.DateField()
    faculty_name = models.CharField(max_length=100,)
    college_code = models.IntegerField()
    college_name = models.CharField(max_length=100)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    def __str__(self):
        return self.name





# Student Exam Model
class StudentExam(models.Model):
    id = models.AutoField(primary_key=True)
    student_info = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    exam_data= models.ForeignKey(ExamData, on_delete=models.CASCADE)
    seat_no = models.IntegerField()

    def __str__(self):
        return f"{self.student_info.name} - {self.exam_data.exam_name}"


# Grade Data Model
class GradeData(models.Model):
    id = models.AutoField(primary_key=True)
    student_exam= models.ForeignKey(StudentExam, on_delete=models.CASCADE)
    subject_bss = models.ForeignKey(BranchSubjectSemester, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2)

    def __str__(self):
        return f"{self.student_exam.student_info.name} - {self.subject_bss.subject.subject_name}: {self.grade}"


# Result Model
class Result(models.Model):
    result_choice=[
        ("Pass","Pass"),
        ("Fail","Fail"),
    ]
    id = models.AutoField(primary_key=True)
    student_exam = models.ForeignKey(StudentExam, on_delete=models.CASCADE)
    # exam_data = models.ForeignKey(ExamData, on_delete=models.CASCADE) #removing this column as we can reference through student_exam model.
    sgpa = models.FloatField()
    cgpa = models.FloatField()
    backlog = models.IntegerField(default=0)
    ufm = models.BooleanField()
    result = models.CharField(choices=result_choice,max_length=4)

    def __str__(self):
        return f"Result of {self.student_exam.student_info.name} - Exam {self.student_exam.exam_data.exam_name}"



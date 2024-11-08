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
    subject_name = models.CharField(max_length=100)
    credits = models.IntegerField()

    def __str__(self):
        return self.subject_name


# Student Info Model
class StudentInfo(models.Model):
    id = models.AutoField(primary_key=True)
    spid = models.IntegerField(unique=True)
    enrollment = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    gender = models.BooleanField()  # True for male, False for female (or consider using CharField with choices)
    date_of_birth = models.DateTimeField()
    faculty_name = models.CharField(max_length=100)
    college_code = models.IntegerField()
    college_name = models.CharField(max_length=100)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# Exam Data Model
class ExamData(models.Model):
    id = models.AutoField(primary_key=True)
    exam_name = models.CharField(max_length=100)
    exam_month = models.IntegerField()
    exam_year = models.IntegerField()
    exam_type = models.IntegerField()
    semester = models.IntegerField()
    declaration_date = models.DateField()
    academic_year = models.IntegerField()

    def __str__(self):
        return self.exam_name


# Student Exam Model
class StudentExam(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    exam = models.ForeignKey(ExamData, on_delete=models.CASCADE)
    seat_no = models.IntegerField()

    def __str__(self):
        return f"{self.student.name} - {self.exam.exam_name}"


# Grade Data Model
class GradeData(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2)

    def __str__(self):
        return f"{self.student.name} - {self.subject.subject_name}: {self.grade}"


# Result Model
class Result(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    exam = models.ForeignKey(ExamData, on_delete=models.CASCADE)
    sgpa = models.FloatField()
    cgpa = models.FloatField()
    backlog = models.IntegerField()
    ufm = models.IntegerField()
    result = models.IntegerField()

    def __str__(self):
        return f"Result of {self.student.name} - Exam {self.exam.exam_name}"


# Branch-Subject-Semester Model
class BranchSubjectSemester(models.Model):
    id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    semester = models.IntegerField()
    is_core = models.BooleanField()
    elective_group = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.branch.branch_name} - {self.subject.subject_name} - Sem {self.semester}"

from django.contrib import admin
from .models import Branch, Subject, ExamData, BranchSubjectSemester, StudentInfo, StudentExam, GradeData, Result

admin.site.register(Branch)
admin.site.register(Subject)
admin.site.register(ExamData)
admin.site.register(BranchSubjectSemester)
admin.site.register(StudentInfo)
admin.site.register(StudentExam)
admin.site.register(GradeData)
admin.site.register(Result)
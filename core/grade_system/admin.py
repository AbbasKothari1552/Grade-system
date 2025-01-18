from django.contrib import admin
from django.db.models import Field
from .models import Branch, Subject, ExamData, StudentInfo, StudentExam, GradeData, Result, CollegeName

#filters
class customFilter(admin.ModelAdmin):
    search_fields=["enrollment","name"]
    #list_display=["spid","name","enrollment","gender","date_of_birth","faculty_name",]
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        # Dynamically set all field names in list_display
        self.list_display = [field.name for field in model._meta.get_fields() if isinstance(field,Field)]
 
admin.site.register(Branch,customFilter)
admin.site.register(Subject,customFilter)
admin.site.register(ExamData,customFilter)
# admin.site.register(BranchSubjectSemester,customFilter)
admin.site.register(CollegeName, customFilter)
admin.site.register(StudentInfo,customFilter)
admin.site.register(StudentExam,customFilter)
admin.site.register(GradeData,customFilter)
admin.site.register(Result,customFilter)
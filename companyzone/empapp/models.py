from django.db import models
from django.core.files.storage import storages # Built-in Django helper

# Create your models here.
class Location(models.Model):
    loc_id = models.IntegerField(primary_key=True)
    loc_name = models.CharField(max_length=30)

    def __str__(self):
        return f"<{self.loc_id}, {self.loc_name}>"
    
    def __repr__(self):
        return self.__str__()
    
class Department(models.Model):
    dept_id = models.IntegerField(primary_key=True)
    dept_name = models.CharField(max_length=30)

    def __str__(self):
        return f"<{self.dept_id}, {self.dept_name}>"
    
    def __repr__(self):
        return self.__str__()

class Employee(models.Model):
    eno = models.IntegerField(primary_key=True)
    ename = models.CharField(max_length=30)
    esal = models.IntegerField()
    epfpic = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    eintvid = models.FileField(upload_to='interview_vids', storage=storages['videos'], null=True, blank=True)
    eresume = models.FileField(upload_to='resumes', storage=storages['raw'], null=True, blank=True)
    edept = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='dept_emp') # Custom reverse relationship name
    eloc = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        permissions = [
            ("view_detail_employee", "Can view single employee detail"),
        ]

class GlobalPermissions(models.Model): 
    class Meta:
        # if we inherit Permission class instead of models.Model
        # proxy = True #Crucial: Tells Django NOT to create a new database table!

        # Define your model-independent permissions here
        permissions = [
            ("view_dept_status", "Can view department status"),
            ("get_emp_form_metadata", "Can get add employee form data"),
        ]
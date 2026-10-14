from django.contrib import admin
from .models import Employee, Department, GlobalPermissions, Location

# Register your models here.
admin.site.register(Employee)
admin.site.register(Department)
admin.site.register(Location)

"""
(Optional but Helpful)
While permissions automatically show up inside the User and Group permission selection boxes after migrating, 
you won't see GlobalPermissions as a separate standalone menu item on the Admin home screen 
unless you register it in your app's admin.py:
"""
# admin.site.register(GlobalPermissions)
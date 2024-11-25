from django.contrib import admin

# Register your models here.
from .models import Profile,Project,Board
# Register your models here.

admin.site.register(Profile)
admin.site.register(Project)
admin.site.register(Board)

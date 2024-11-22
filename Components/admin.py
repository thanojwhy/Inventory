from django.contrib import admin
from .models import Component
from .models import Usage
# Register your models here.

admin.site.register(Component)
admin.site.register(Usage)
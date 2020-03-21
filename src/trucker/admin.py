from django.contrib import admin
from .models import truck_company, trucks, driver
# Register your models here.

admin.site.register(truck_company)
admin.site.register(trucks)
admin.site.register(driver)

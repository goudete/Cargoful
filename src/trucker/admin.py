from django.contrib import admin
from .models import truck_company, trucks, driver, counter_offer
# Register your models here.

admin.site.register(truck_company)
admin.site.register(trucks)
admin.site.register(driver)
admin.site.register(counter_offer)

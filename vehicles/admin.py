from django.contrib import admin
from .models import Branch, TransferCost, Vehicle, Reservation, Assignment, MaintenanceLog


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'title']
    list_editable = ['title']
    search_fields = ['name', 'title']


admin.site.register(TransferCost)
admin.site.register(Vehicle)
admin.site.register(Reservation)
admin.site.register(Assignment)
admin.site.register(MaintenanceLog)

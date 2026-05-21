from django.contrib import admin
from .models import OperatorReturn, LicenceReturn, VehicleEmission, VehicleAccessibility


class LicenceInline(admin.TabularInline):
    model = LicenceReturn
    extra = 0


class EmissionInline(admin.TabularInline):
    model = VehicleEmission
    extra = 0


class AccessibilityInline(admin.TabularInline):
    model = VehicleAccessibility
    extra = 0


@admin.register(OperatorReturn)
class OperatorReturnAdmin(admin.ModelAdmin):
    list_display = ['operator_name', 'data_year', 'county', 'status', 'submitted_at']
    list_filter = ['status', 'data_year', 'county']
    search_fields = ['operator_name', 'trading_name']
    inlines = [LicenceInline, EmissionInline, AccessibilityInline]
    readonly_fields = ['created_at', 'updated_at', 'submitted_at']

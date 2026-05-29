from django.contrib import admin
from django.utils.html import format_html
from .models import OperatorReturn, LicenceReturn, VehicleEmission, VehicleAccessibility, OperatorAccess


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


@admin.register(OperatorAccess)
class OperatorAccessAdmin(admin.ModelAdmin):
    list_display = [
        'operator_name', 'operator_email',
        'token_box', 'is_active',
        'return_status', 'created_at', 'last_accessed_at',
    ]
    list_filter = ['is_active']
    search_fields = ['operator_name', 'operator_email']
    readonly_fields = ['token', 'token_box', 'created_at', 'last_accessed_at']
    fields = ['operator_name', 'operator_email', 'is_active', 'token', 'token_box', 'operator_return', 'created_at', 'last_accessed_at']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['operator_name', 'operator_email']
        return self.readonly_fields

    @admin.display(description='Access Token — copy and email this to the operator')
    def token_box(self, obj):
        if not obj or not obj.token:
            return '—'
        return format_html(
            '<code style="'
            'background:#f0f4ff;border:1px solid #c5d0e8;border-radius:4px;'
            'padding:4px 10px;font-size:0.9em;letter-spacing:0.02em;'
            'user-select:all;cursor:text;"'
            '>{}</code>',
            obj.token,
        )

    @admin.display(description='Return Status')
    def return_status(self, obj):
        if not obj.operator_return:
            return format_html('<span style="color:#999;">No return yet</span>')
        r = obj.operator_return
        colour = '#1a7a4a' if r.status == 'submitted' else '#1B3A6B'
        return format_html(
            '<span style="color:{};">{} ({})</span>',
            colour, r.operator_name, r.get_status_display(),
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

from django.contrib import admin
from .models import AdminProfile, BirthdayTemplate, Communication


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title', 'phone_number')
    search_fields = ('user__username', 'user__email', 'job_title')
    list_filter = ('job_title',)


@admin.register(BirthdayTemplate)
class BirthdayTemplateAdmin(admin.ModelAdmin):
    list_display = ('get_month_display', 'title', 'is_active', 'created_by', 'created_date')
    list_filter = ('month', 'is_active', 'created_date')
    search_fields = ('title', 'message')
    readonly_fields = ('created_date', 'updated_date', 'created_by')
    ordering = ('month',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('month', 'title', 'message', 'is_active')
        }),
        ('Styling', {
            'fields': ('emoji', 'background_color', 'text_color', 'border_color'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'communication_type', 'sender', 'sent_date', 'recipient_count')
    list_filter = ('communication_type', 'sent_date')
    search_fields = ('title', 'message', 'sender__username')
    readonly_fields = ('sent_date', 'sender')
    filter_horizontal = ('recipients',)
    
    def recipient_count(self, obj):
        return obj.recipients.count()
    recipient_count.short_description = 'Recipients'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.sender = request.user
        super().save_model(request, obj, form, change)

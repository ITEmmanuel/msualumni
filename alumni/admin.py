from django.contrib import admin
from .models import AlumniStory, SocialLink, Donation, Alumni


@admin.register(AlumniStory)
class AlumniStoryAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_date", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "author")
    ordering = ("-published_date",)


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("name", "platform", "url", "order", "is_active")
    list_filter = ("platform", "is_active")
    search_fields = ("name", "platform")
    ordering = ("order",)


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "amount", "currency", "timestamp")
    list_filter = ("currency",)
    search_fields = ("name", "email")
    ordering = ("-timestamp",)


class BirthdayTodayFilter(admin.SimpleListFilter):
    title = 'Birthday Today'
    parameter_name = 'birthday_today'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            today = timezone.localdate()
            return queryset.filter(date_of_birth__month=today.month, date_of_birth__day=today.day)
        return queryset


class BirthMonthFilter(admin.SimpleListFilter):
    title = 'Birth Month'
    parameter_name = 'birth_month'

    def lookups(self, request, model_admin):
        import calendar
        return [(str(i), calendar.month_name[i]) for i in range(1, 13)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date_of_birth__month=int(self.value()))
        return queryset


@admin.register(Alumni)
class AlumniAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "date_of_birth", "graduation_year")
    search_fields = ("first_name", "last_name", "email", "reg_number")
    list_filter = (BirthdayTodayFilter, BirthMonthFilter, "graduation_year")

class DonationAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "amount", "currency", "timestamp")
    list_filter = ("currency",)
    search_fields = ("name", "email")
    ordering = ("-timestamp",)

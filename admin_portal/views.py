from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Count
from .forms import AdminLoginForm, NewsletterForm, EventForm, CommunicationForm, BirthdayTemplateForm
from alumni.models import Alumni, Newsletter, Event
from .models import Communication, BirthdayTemplate
from django.urls import reverse_lazy
from django.utils import timezone


class AdminLogoutView(LogoutView):
    """Logout view that accepts GET or POST so sidebar link works."""
    next_page = reverse_lazy('admin_portal:login')
    http_method_names = ['get', 'post', 'head', 'options']


class AdminLoginView(LoginView):
    template_name = 'admin_portal/login.html'
    form_class = AdminLoginForm
    success_url = reverse_lazy('admin_portal:dashboard')


@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    def get(self, request):
        alumni_count = Alumni.objects.count()
        verified_alumni_count = Alumni.objects.filter(is_verified=True).count()
        recent_alumni = Alumni.objects.order_by('-registration_date')[:5]
        newsletter_count = Newsletter.objects.count()
        event_count = Event.objects.count()
        
        context = {
            'alumni_count': alumni_count,
            'verified_alumni_count': verified_alumni_count,
            'recent_alumni': recent_alumni,
            'newsletter_count': newsletter_count,
            'event_count': event_count,
        }
        
        return render(request, 'admin_portal/dashboard.html', context)


@method_decorator(login_required, name='dispatch')
class AlumniListView(View):
    def get(self, request):
        alumni = Alumni.objects.all().order_by('-registration_date')
        return render(request, 'admin_portal/alumni_list.html', {'alumni': alumni})


@method_decorator(login_required, name='dispatch')
class AlumniDetailView(View):
    def get(self, request, pk):
        alumni = get_object_or_404(Alumni, pk=pk)
        return render(request, 'admin_portal/alumni_detail.html', {'alumni': alumni})


@method_decorator(login_required, name='dispatch')
class VerifyAlumniView(View):
    def post(self, request, pk):
        alumni = get_object_or_404(Alumni, pk=pk)
        alumni.is_verified = not alumni.is_verified
        alumni.save()
        status = "verified" if alumni.is_verified else "unverified"
        messages.success(request, f"Alumni {alumni.reg_number} has been {status}.")
        return redirect('admin_portal:alumni_detail', pk=pk)


@method_decorator(login_required, name='dispatch')
class NewsletterListView(View):
    def get(self, request):
        newsletters = Newsletter.objects.all().order_by('-published_date')
        return render(request, 'admin_portal/newsletter_list.html', {'newsletters': newsletters})


@method_decorator(login_required, name='dispatch')
class CreateNewsletterView(View):
    def get(self, request):
        form = NewsletterForm()
        return render(request, 'admin_portal/create_newsletter.html', {'form': form})
    
    def post(self, request):
        form = NewsletterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Newsletter created successfully!")
            return redirect('admin_portal:newsletters')
        return render(request, 'admin_portal/create_newsletter.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class EditNewsletterView(View):
    def get(self, request, pk):
        newsletter = get_object_or_404(Newsletter, pk=pk)
        form = NewsletterForm(instance=newsletter)
        return render(request, 'admin_portal/edit_newsletter.html', {'form': form, 'newsletter': newsletter})
    
    def post(self, request, pk):
        newsletter = get_object_or_404(Newsletter, pk=pk)
        form = NewsletterForm(request.POST, request.FILES, instance=newsletter)
        if form.is_valid():
            form.save()
            messages.success(request, "Newsletter updated successfully!")
            return redirect('admin_portal:newsletters')
        return render(request, 'admin_portal/edit_newsletter.html', {'form': form, 'newsletter': newsletter})


@method_decorator(login_required, name='dispatch')
class EventListView(View):
    def get(self, request):
        events = Event.objects.all().order_by('-date')
        context = {
            'events': events,
            'now': timezone.now(),
        }
        return render(request, 'admin_portal/event_list.html', context)


@method_decorator(login_required, name='dispatch')
class BirthdayListView(View):
    """List alumni with birthdays today and upcoming birthdays within next 30 days."""
    def get(self, request):
        from datetime import timedelta
        today = timezone.localdate()
        upcoming_limit = today + timedelta(days=30)

        today_birthdays = []
        upcoming_birthdays = []

        # Get birthday templates for better display
        birthday_templates = {}
        for template in BirthdayTemplate.objects.filter(is_active=True):
            birthday_templates[template.month] = template

        alumni_qs = Alumni.objects.filter(date_of_birth__isnull=False)
        for alum in alumni_qs:
            dob = alum.date_of_birth
            if not dob:
                continue
            try:
                next_bd = dob.replace(year=today.year)
            except ValueError:
                # handle Feb 29 on non-leap year -> move to Mar 1
                next_bd = dob.replace(year=today.year, day=1, month=3)
            if next_bd < today:
                # birthday already occurred this year; use next year
                try:
                    next_bd = dob.replace(year=today.year + 1)
                except ValueError:
                    next_bd = dob.replace(year=today.year + 1, day=1, month=3)

            # Attach template info for this alumni's birthday month
            template = birthday_templates.get(next_bd.month)
            setattr(alum, 'birthday_template', template)

            if next_bd == today:
                today_birthdays.append(alum)
            elif today < next_bd <= upcoming_limit:
                # attach attribute for template use
                setattr(alum, 'next_birthday', next_bd)
                upcoming_birthdays.append(alum)

        upcoming_birthdays.sort(key=lambda x: x.next_birthday)

        context = {
            'today_birthdays': today_birthdays,
            'upcoming_birthdays': upcoming_birthdays,
            'birthday_templates': birthday_templates,
        }
        return render(request, 'admin_portal/birthday_list.html', context)


@method_decorator(login_required, name='dispatch')
class CreateEventView(View):
    def get(self, request):
        form = EventForm()
        return render(request, 'admin_portal/create_event.html', {'form': form})
    
    def post(self, request):
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Event created successfully!")
            return redirect('admin_portal:events')
        return render(request, 'admin_portal/create_event.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class EditEventView(View):
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        form = EventForm(instance=event)
        return render(request, 'admin_portal/edit_event.html', {'form': form, 'event': event})
    
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('admin_portal:events')
        return render(request, 'admin_portal/edit_event.html', {'form': form, 'event': event})


@method_decorator(login_required, name='dispatch')
class ReportsView(View):
    """Display aggregated alumni reports by country and areas of interest."""
    @method_decorator(login_required)
    def get(self, request):
        # Alumni by country
        country_counts = Alumni.objects.values('country').annotate(total=Count('id')).order_by('-total')

        # Alumni by areas of interest (boolean fields)
        interest_mapping = {
            'Networking/Peer Engagement': 'interest_networking',
            'Academic & Mentorship': 'interest_academic',
            'Career & Professional Development': 'interest_career',
            'Giving Back': 'interest_giving_back',
            'Stay Informed': 'interest_stay_informed',
        }
        interest_counts = {
            label: Alumni.objects.filter(**{field: True}).count()
            for label, field in interest_mapping.items()
        }

        context = {
            'country_counts': country_counts,
            'interest_counts': interest_counts,
        }
        return render(request, 'admin_portal/reports.html', context)


class CommunicationView(View):
    def get(self, request):
        form = CommunicationForm()
        communications = Communication.objects.all().order_by('-sent_date')
        return render(request, 'admin_portal/communication.html', {'form': form, 'communications': communications})
    
    def post(self, request):
        form = CommunicationForm(request.POST)
        if form.is_valid():
            comm = form.save(commit=False)
            comm.sender = request.user
            comm.save()
            
            # Handle recipients
            if form.cleaned_data['all_alumni']:
                alumni = Alumni.objects.all()
                for alum in alumni:
                    comm.recipients.add(alum)
            
            messages.success(request, "Communication sent successfully!")
            return redirect('admin_portal:communication')
        
        communications = Communication.objects.all().order_by('-sent_date')
        return render(request, 'admin_portal/communication.html', {'form': form, 'communications': communications})


@method_decorator(login_required, name='dispatch')
class BirthdayTemplateListView(View):
    """List all birthday templates organized by month."""
    def get(self, request):
        templates = BirthdayTemplate.objects.all().order_by('month')
        
        # Create a dict with all months, showing which have templates
        template_dict = {}
        for month_num, month_name in BirthdayTemplate.MONTH_CHOICES:
            template_dict[month_num] = {
                'name': month_name,
                'template': None
            }
        
        # Fill in existing templates
        for template in templates:
            template_dict[template.month]['template'] = template
        
        context = {
            'template_dict': template_dict,
            'templates': templates,
        }
        return render(request, 'admin_portal/birthday_template_list.html', context)


@method_decorator(login_required, name='dispatch')
class CreateBirthdayTemplateView(View):
    """Create a new birthday template."""
    def get(self, request):
        form = BirthdayTemplateForm()
        return render(request, 'admin_portal/create_birthday_template.html', {'form': form})
    
    def post(self, request):
        form = BirthdayTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = request.user
            template.save()
            messages.success(request, f"Birthday template for {template.get_month_display()} created successfully!")
            return redirect('admin_portal:birthday_templates')
        return render(request, 'admin_portal/create_birthday_template.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class EditBirthdayTemplateView(View):
    """Edit an existing birthday template."""
    def get(self, request, pk):
        template = get_object_or_404(BirthdayTemplate, pk=pk)
        form = BirthdayTemplateForm(instance=template)
        return render(request, 'admin_portal/edit_birthday_template.html', {'form': form, 'template': template})
    
    def post(self, request, pk):
        template = get_object_or_404(BirthdayTemplate, pk=pk)
        form = BirthdayTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, f"Birthday template for {template.get_month_display()} updated successfully!")
            return redirect('admin_portal:birthday_templates')
        return render(request, 'admin_portal/edit_birthday_template.html', {'form': form, 'template': template})


@method_decorator(login_required, name='dispatch')
class DeleteBirthdayTemplateView(View):
    """Delete a birthday template."""
    def post(self, request, pk):
        template = get_object_or_404(BirthdayTemplate, pk=pk)
        month_name = template.get_month_display()
        template.delete()
        messages.success(request, f"Birthday template for {month_name} deleted successfully!")
        return redirect('admin_portal:birthday_templates')

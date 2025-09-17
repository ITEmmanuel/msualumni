from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from .audit_helpers import create_alumni_audit_log
from .forms import AlumniRegistrationForm, AlumniFullUpdateForm, DonationForm
from .models import AlumniStory, SocialLink
from .models import Alumni, Newsletter, Event, IAROContent
from django.utils import timezone
import pycountry
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest
import json

class HomePageView(View):
    def get(self, request):
        newsletters = Newsletter.objects.order_by('-published_date')[:3]
        upcoming_events = Event.objects.filter(date__gte=timezone.now()).order_by('date')[:3]
        
        # Get active IARO content with its objectives
        iaro_content = IAROContent.objects.filter(is_active=True).first()
        
        context = {
            'newsletters': newsletters,
            'upcoming_events': upcoming_events,
            'iaro': iaro_content,
        }
        return render(request, 'alumni/home.html', context)


class RegistrationView(View):
    @staticmethod
    def get_client_ip(request):
        """Get the client's IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
        
    def get(self, request):
        form = AlumniRegistrationForm()
        
        # Load all ISO countries (alpha_2 code + common name)
        countries_sorted = sorted(
            (
                {
                    'code': c.alpha_2,
                    'name': getattr(c, 'common_name', None) or getattr(c, 'name', '')
                }
                for c in pycountry.countries
            ),
            key=lambda x: x['name']
        )
        
        context = {
            'form': form,
            'now': timezone.now(),
            'countries': countries_sorted,
            'year_choices': list(range(2000, timezone.now().year + 3))
        }
        return render(request, 'alumni/registration.html', context)
    
    def post(self, request):
        form = AlumniRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            alumni = form.save(commit=False)
            
            # Handle the country and city fields from Select2
            country_code = request.POST.get('country')
            if country_code:
                try:
                    country_obj = pycountry.countries.get(alpha_2=country_code)
                    if country_obj:
                        alumni.country = getattr(country_obj, 'common_name', None) or country_obj.name
                except Exception:
                    pass
            
            # Handle city (can be a predefined value or custom input)
            city = request.POST.get('city')
            if city:
                alumni.city = city
            
            alumni.is_verified = False  # Set to False until email verification is implemented
            
            # Add request to instance for audit logging
            setattr(alumni, '_request', request)
            setattr(alumni, '_change_reason', 'New alumni registration')
            
            try:
                alumni.save()
                
                # Log the registration using our custom helper to avoid AnonymousUser errors
                create_alumni_audit_log(
                    alumni=alumni,
                    action='create',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    changed_fields={
                        'status': 'New registration',
                        'email': alumni.email,
                        'registration_date': alumni.registration_date.isoformat()
                    },
                    reason='New alumni registration through public form'
                )
                
                # Send verification email (to be implemented)
                # send_verification_email(alumni)
                
                messages.success(
                    request,
                    "Registration submitted successfully! You will receive a verification email shortly. "
                    "Please check your inbox and verify your email address."
                )
                return redirect('alumni:success')
                
            except Exception as e:
                # Debug print to see the actual error
                print(f"REGISTRATION ERROR: {e}")
                # Only log if alumni was created
                if alumni and getattr(alumni, 'pk', None):
                    try:
                        # Log the error using our custom helper to avoid AnonymousUser errors
                        create_alumni_audit_log(
                            alumni=alumni,
                            action='error',
                            ip_address=self.get_client_ip(request),
                            user_agent=request.META.get('HTTP_USER_AGENT', ''),
                            changed_fields={
                                'error': str(e),
                                'form_data': {k: str(v) for k, v in form.cleaned_data.items()}
                            },
                            reason='Error during alumni registration'
                        )
                    except Exception as log_error:
                        print(f"Failed to create audit log: {log_error}")
                messages.error(
                    request,
                    "An error occurred during registration. Please try again or contact support if the problem persists."
                )
                # Add all necessary context for the form template
                countries_sorted = sorted(
                    (
                        {
                            'code': c.alpha_2,
                            'name': getattr(c, 'common_name', None) or getattr(c, 'name', '')
                        }
                        for c in pycountry.countries
                    ),
                    key=lambda x: x['name']
                )
                context = {
                    'form': form,
                    'now': timezone.now(),
                    'countries': countries_sorted,
                    'year_choices': list(range(2000, timezone.now().year + 3))
                }
                return render(request, 'alumni/registration.html', context)
            
        # Get the same context as in get() method
        countries_sorted = sorted(
            (
                {
                    'code': c.alpha_2,
                    'name': getattr(c, 'common_name', None) or getattr(c, 'name', '')
                }
                for c in pycountry.countries
            ),
            key=lambda x: x['name']
        )
        context = {
            'form': form,
            'now': timezone.now(),
            'countries': countries_sorted,
            'year_choices': list(range(2000, timezone.now().year + 3))
        }
        return render(request, 'alumni/registration.html', context)


# Removed BioFormView as we've combined both forms into one


class SuccessView(View):
    def get(self, request):
        return render(request, 'alumni/success.html')


class NewslettersView(View):
    def get(self, request):
        year = request.GET.get('year')
        newsletters_qs = Newsletter.objects.all()
        if year and year.isdigit():
            newsletters_qs = newsletters_qs.filter(published_date__year=year)
        newsletters = newsletters_qs.order_by('-published_date')

        years = Newsletter.objects.dates('published_date', 'year', order='DESC')
        context = {
            'newsletters': newsletters,
            'years': [d.year for d in years],
            'selected_year': int(year) if year and year.isdigit() else None,
        }
        return render(request, 'alumni/newsletters.html', context)


class NewsletterDetailView(View):
    def get(self, request, pk):
        newsletter = get_object_or_404(Newsletter, pk=pk)
        return render(request, 'alumni/newsletter_detail.html', {'newsletter': newsletter})


class EventsView(View):
    def get(self, request):
        events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
        past_events = Event.objects.filter(date__lt=timezone.now()).order_by('-date')
        
        context = {
            'events': events,
            'past_events': past_events,
        }
        return render(request, 'alumni/events.html', context)


class EventDetailView(View):
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        context = {
            'event': event,
            'now': timezone.now(),
        }
        return render(request, 'alumni/event_detail.html', context)


# ------------------ Self-service Update Flow ------------------

class QuickUpdateView(View):
    """Single-page update: alumni submits National ID plus any fields to change."""
    template_name = 'alumni/update.html'

    def get(self, request):
        context = {
            'full_form': AlumniFullUpdateForm()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        update_type = request.POST.get('update_type', 'quick')
        national_id = request.POST.get('national_id', '').strip()
        if not national_id:
            messages.error(request, 'National ID is required.')
            return render(request, self.template_name, {'full_form': AlumniFullUpdateForm()})

        try:
            alumni = Alumni.objects.get(national_id=national_id)
        except Alumni.DoesNotExist:
            messages.error(request, 'No alumni record found with that National ID. You can register instead.')
            context = {'register_url': 'alumni:register', 'full_form': AlumniFullUpdateForm()}
            return render(request, self.template_name, context)

        # If user chose full update, delegate to form
        if update_type == 'full':
            try:
                alumni = Alumni.objects.get(national_id=national_id)
            except Alumni.DoesNotExist:
                messages.error(request, 'No alumni record found with that National ID. You can register instead.')
                context = {'full_form': AlumniFullUpdateForm(request.POST)}
                return render(request, self.template_name, context)
            form = AlumniFullUpdateForm(request.POST, request.FILES, instance=alumni)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('alumni:quick_update')
            context = {'full_form': form}
            return render(request, self.template_name, context)

        # quick update path
        changed_fields = {}
        updatable = ['employment_status', 'current_employer', 'job_title', 'industry',
                     'email', 'mobile_number', 'city', 'country', 'bio']
        for field in updatable:
            value = request.POST.get(field, '').strip()
            if value:
                original = getattr(alumni, field)
                if original != value:
                    changed_fields[field] = {'old': original, 'new': value}
                    setattr(alumni, field, value)

        if 'profile_picture' in request.FILES:
            alumni.profile_picture = request.FILES['profile_picture']
            changed_fields['profile_picture'] = 'updated'

        if changed_fields:
            alumni.save()
            # Optional audit log
            try:
                create_alumni_audit_log(
                    alumni=alumni,
                    action='update',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    changed_fields=changed_fields,
                    reason='Quick update form'
                )
            except Exception as e:
                print('Audit log error:', e)

        messages.success(request, 'Your details have been updated successfully.')
        return redirect('alumni:quick_update')


class UpdateLookupView(View):
    """Step 1: Ask for national ID and desired update type, then redirect."""
    template_name = 'alumni/update_lookup.html'

    def get(self, request):
        return render(request, self.template_name, {'full_form': AlumniFullUpdateForm()})

    def post(self, request):
        update_type = request.POST.get('update_type', 'quick')
        national_id = request.POST.get('national_id', '').strip()
        # not used here
        if not national_id:
            messages.error(request, 'Please enter your National ID / Passport number.')
            return render(request, self.template_name, {'full_form': AlumniFullUpdateForm()})
        try:
            alumni = Alumni.objects.get(national_id=national_id)
        except Alumni.DoesNotExist:
            messages.error(request, 'No alumni record found with that National ID. Would you like to register first?')
            return render(request, self.template_name, {
                'registration_url': 'alumni:register'
            })
        if update_type == 'full':
            return redirect('alumni:update_full', pk=alumni.pk)
        return redirect('alumni:update_employment', pk=alumni.pk)


class EmploymentUpdateView(View):
    """Allow alumni to update only employment info."""
    template_name = 'alumni/update_employment.html'

    def get_object(self, pk):
        return get_object_or_404(Alumni, pk=pk)

    def get(self, request, pk):
        alumni = self.get_object(pk)
        form = AlumniEmploymentUpdateForm(instance=alumni)
        return render(request, self.template_name, {'form': form})

    def post(self, request, pk):
        alumni = self.get_object(pk)
        form = AlumniEmploymentUpdateForm(request.POST, instance=alumni)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employment details updated successfully.')
            return redirect('alumni:update_employment', pk=pk)
        return render(request, self.template_name, {'form': form})


class FullUpdateView(View):
    """Allow alumni to update the majority of their profile."""
    template_name = 'alumni/update_full.html'

    def get_object(self, pk):
        return get_object_or_404(Alumni, pk=pk)

    def get(self, request, pk):
        alumni = self.get_object(pk)
        # Reuse registration form but bind existing instance
        form = AlumniRegistrationForm(instance=alumni)
        # National ID and email shouldn’t be changed easily
        form.fields['national_id'].widget.attrs['readonly'] = True
        form.fields['email'].widget.attrs['readonly'] = True
        return render(request, self.template_name, {'form': form})

    def post(self, request, pk):
        alumni = self.get_object(pk)
        form = AlumniRegistrationForm(request.POST, request.FILES, instance=alumni)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('alumni:update_full', pk=pk)
        return render(request, self.template_name, {'form': form})


# ------------------ Alumni Engagement Pages ------------------
class StoriesView(View):
    """Display inspiring alumni stories."""
    template_name = 'alumni/stories.html'

    def get(self, request):
        stories = AlumniStory.objects.filter(is_published=True)
        return render(request, self.template_name, {"stories": stories})


class ConnectView(View):
    """Show social / messaging groups alumni can join."""
    template_name = 'alumni/connect.html'

    def get(self, request):
        links = SocialLink.objects.filter(is_active=True)
        return render(request, self.template_name, {"links": links})


class DonateView(View):
    """Allow alumni to pledge a donation."""
    template_name = 'alumni/donate.html'

    def get(self, request):
        form = DonationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = DonationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your generous contribution!')
            return redirect('alumni:donate')
        return render(request, self.template_name, {'form': form})
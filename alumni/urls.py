from django.urls import path
from . import views

app_name = 'alumni'

urlpatterns = [
    path('update/', views.QuickUpdateView.as_view(), name='quick_update'),
    path('update/<int:pk>/employment/', views.EmploymentUpdateView.as_view(), name='update_employment'),
    path('update/<int:pk>/full/', views.FullUpdateView.as_view(), name='update_full'),
    path('', views.HomePageView.as_view(), name='home'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('success/', views.SuccessView.as_view(), name='success'),
    path('newsletters/', views.NewslettersView.as_view(), name='newsletters'),
    path('newsletters/<int:pk>/', views.NewsletterDetailView.as_view(), name='newsletter_detail'),
    path('events/', views.EventsView.as_view(), name='events'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('stories/', views.StoriesView.as_view(), name='stories'),
    path('connect/', views.ConnectView.as_view(), name='connect'),
    path('donate/', views.DonateView.as_view(), name='donate'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
]
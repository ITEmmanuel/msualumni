from django.urls import path
# from django.contrib.auth.views import LogoutView
from .views import AdminLogoutView
from . import views

app_name = 'admin_portal'

urlpatterns = [
    path('login/', views.AdminLoginView.as_view(), name='login'),
    path('logout/', AdminLogoutView.as_view(), name='logout'),
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('alumni/', views.AlumniListView.as_view(), name='alumni_list'),
    path('alumni/<int:pk>/', views.AlumniDetailView.as_view(), name='alumni_detail'),
    path('alumni/<int:pk>/verify/', views.VerifyAlumniView.as_view(), name='verify_alumni'),
    path('newsletters/', views.NewsletterListView.as_view(), name='newsletters'),
    path('newsletters/create/', views.CreateNewsletterView.as_view(), name='create_newsletter'),
    path('newsletters/<int:pk>/edit/', views.EditNewsletterView.as_view(), name='edit_newsletter'),
    path('events/', views.EventListView.as_view(), name='events'),
    path('events/create/', views.CreateEventView.as_view(), name='create_event'),
    path('events/<int:pk>/edit/', views.EditEventView.as_view(), name='edit_event'),
    path('communication/', views.CommunicationView.as_view(), name='communication'),
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('birthdays/', views.BirthdayListView.as_view(), name='birthdays'),
    path('birthday-templates/', views.BirthdayTemplateListView.as_view(), name='birthday_templates'),
    path('birthday-templates/create/', views.CreateBirthdayTemplateView.as_view(), name='create_birthday_template'),
    path('birthday-templates/<int:pk>/edit/', views.EditBirthdayTemplateView.as_view(), name='edit_birthday_template'),
    path('birthday-templates/<int:pk>/delete/', views.DeleteBirthdayTemplateView.as_view(), name='delete_birthday_template'),
]
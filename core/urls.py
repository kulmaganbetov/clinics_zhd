from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('doctors/', views.DoctorsView.as_view(), name='doctors'),
    path('doctors/<int:pk>/', views.DoctorDetailView.as_view(), name='doctor_detail'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<slug:slug>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]

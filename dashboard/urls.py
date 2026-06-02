from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('user/', views.user_dashboard, name='user'),
    path('technician/', views.technician_dashboard, name='technician'),
    path('admin/', views.admin_dashboard, name='admin'),
]

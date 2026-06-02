from django.urls import path
from . import views

app_name = 'technicians'

urlpatterns = [
    path('', views.technician_list, name='list'),
    path('create/', views.technician_create, name='create'),
    path('<int:pk>/edit/', views.technician_edit, name='edit'),
]

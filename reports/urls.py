from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_index, name='index'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/json/', views.export_json, name='export_json'),
]

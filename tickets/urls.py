from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.ticket_list, name='list'),
    path('create/', views.ticket_create, name='create'),
    path('<int:pk>/', views.ticket_detail, name='detail'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('<int:pk>/status/', views.update_status, name='update_status'),
    path('<int:pk>/assign/', views.assign_ticket, name='assign'),
    path('<int:pk>/close/', views.close_ticket, name='close'),
]

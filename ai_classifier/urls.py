from django.urls import path
from . import views

app_name = 'ai_classifier'

urlpatterns = [
    path('classify/', views.classify_view, name='classify'),
]

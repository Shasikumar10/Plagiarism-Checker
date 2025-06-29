from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('result/', views.result, name='result'),
    path('download/', views.download_pdf_report, name='download_report'),  # 🔧 This line fixes the issue
]

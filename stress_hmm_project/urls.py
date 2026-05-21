# stress_hmm_project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('academic.urls')),  # Ahora es academic directamente
]
from django.urls import path

from taschoolassistant.core.views import health_check

urlpatterns = [
    # ... your other url patterns
    path('health/', health_check, name='health_check'),
    # Or path('ping/', views.health_check, name='health_check'),
]
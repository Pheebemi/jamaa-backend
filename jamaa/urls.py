from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/cases/', include('apps.cases.urls')),
    path('api/sync/', include('apps.sync.urls')),
    path('api/alerts/', include('apps.alerts.urls')),
    path('api/ai/', include('apps.ai.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
]

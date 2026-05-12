from django.urls import path
from .views import AlertListView, AlertBroadcastView

urlpatterns = [
    path('', AlertListView.as_view(), name='alerts'),
    path('broadcast/', AlertBroadcastView.as_view(), name='alert-broadcast'),
]

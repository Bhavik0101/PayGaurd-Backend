from django.urls import path
from .import views
urlpatterns = [
    path('',views.FraudDetail.as_view())
]

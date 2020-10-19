from django.urls import path
from . import views


urlpatterns = [
    path('get/', views.GetUserAPI.as_view(), name='get_user'),
]

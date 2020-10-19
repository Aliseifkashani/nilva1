from django.urls import path
from . import views


urlpatterns = [
    path('add/', views.AddNotificationAPI.as_view(), name='add_notification'),
    path('edit/', views.EditNotificationAPI.as_view(), name='edit_notification'),
    path('delete/', views.DeleteNotificationAPI.as_view(), name='delete_notification'),
    path('get/', views.GetNotificationAPI.as_view(), name='get_notification'),
]

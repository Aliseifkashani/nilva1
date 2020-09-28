from django.urls import path
from . import views


urlpatterns = [
    # path('author/', views.authorization, name='test'),
    path('create/', views.CreateUserAPIView.as_view(), name='create_user'),
    # path('obtain_token/', views.authenticate_user, name='obtain_token'),
    path('update/', views.UserRetrieveUpdateAPIView.as_view(), name='update'),
    path('add/', views.AddNotificationAPI.as_view(), name='add_notification'),
    path('edit/', views.EditNotificationAPI.as_view(), name='edit_notification'),
    path('delete/', views.DeleteNotificationAPI.as_view(), name='delete_notification'),
    path('get/', views.GetNotificationAPI.as_view(), name='get_notification'),
]

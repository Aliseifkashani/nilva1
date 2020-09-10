from django.urls import path
from . import views


urlpatterns = [
    path('author/', views.authorization, name='test'),
    path('create/', views.CreateUserAPIView.as_view(), name='create_user'),
    path('obtain_token/', views.authenticate_user, name='obtain_token'),
    path('update/', views.UserRetrieveUpdateAPIView.as_view(), name='update'),
    path('add/', views.add_notif, name='add_notification'),
    path('edit/', views.edit_notif, name='edit_notification'),
]

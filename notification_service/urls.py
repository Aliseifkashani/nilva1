from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from . import test_views


urlpatterns = [
    path('notification/', include('notification.urls'), name='notifications'),
    path('user/', include('user.urls'), name='user'),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('test-email/', test_views.test_send_email_to_multiple_people, name='test_send_email_to_multiple_people'),
    path('educational/', test_views.educational, name='educational'),
]

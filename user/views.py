from rest_framework.generics import ListAPIView

from user.models import User
from user.serializers import UserSerializer


class GetUserAPI(ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

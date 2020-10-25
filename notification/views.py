from time import sleep

from django.http import JsonResponse
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView, DestroyAPIView, ListAPIView
from rest_framework.response import Response

from notification.serializers import NotificationSerializer
from .models import Notification
from . import tasks


class GetNotificationAPI(ListAPIView):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()


class AddNotificationAPI(ListCreateAPIView):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = NotificationSerializer(data=request.data)
        if not serializer.is_valid():

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        tasks.add_notif_task(serializer)

        data = serializer.data
        data['due_date'] = serializer.data['due_date'].replace('T', ' ')[:-9]
        data['time_to_send'] = serializer.data['time_to_send'].replace('T', ' ')[:-9]
        return JsonResponse(data)


class EditNotificationAPI(RetrieveUpdateAPIView):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()

    def patch(self, request, *args, **kwargs):
        id = request.data['id']
        notif = Notification.objects.get(id=id)
        serializer = NotificationSerializer(notif, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        tasks.edit_notif_task(serializer)

        data = serializer.data
        data['due_date'] = serializer.data['due_date'].replace('T', ' ')[:-9]
        data['time_to_send'] = serializer.data['time_to_send'].replace('T', ' ')[:-9]
        return JsonResponse(data)


class DeleteNotificationAPI(DestroyAPIView):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()

    def delete(self, request, *args, **kwargs):
        if not 'id' in request.data or (
                'id' in request.data and not Notification.objects.filter(id=request.data['id'])):
            return Response("id field isn't provided or invalid id", status=status.HTTP_400_BAD_REQUEST)
        notif = Notification.objects.get(id=request.data['id'])
        serializer = NotificationSerializer(notif)

        tasks.delete_notif_task(serializer)
        notif.delete()

        data = NotificationSerializer(notif).data
        data['due_date'] = serializer.data['due_date'].replace('T', ' ')[:-9]
        data['time_to_send'] = serializer.data['time_to_send'].replace('T', ' ')[:-9]
        return JsonResponse(data)

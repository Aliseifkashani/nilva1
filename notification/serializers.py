from rest_framework import serializers
from notification.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        exclude = ('task_id',)

    # if we have other irrelevant data in our request's body, it ignores it and acts well
    def create(self, validated_data):
        return Notification.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.creator = validated_data.get('creator', instance.creator)
        instance.relevant_staff = validated_data.get('relevant_staff', instance.relevant_staff)
        instance.time_created = validated_data.get('time_created', instance.time_created)
        instance.time_to_send = validated_data.get('time_to_send', instance.time_to_send)
        instance.notification_types = validated_data.get('notification_types', instance.notification_types)
        instance.repeat = validated_data.get('repeat', instance.repeat)
        instance.interval = validated_data.get('interval', instance.interval)
        instance.task_id = validated_data.get('task_id', instance.task_id)
        instance.save()

        return instance

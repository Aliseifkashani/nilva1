import ast
from kavenegar import *
import jwt
from django.contrib.auth import user_logged_in
from django.http import HttpResponse, JsonResponse
# from .models import User as Main_User
from django.contrib.auth.models import User
from rest_framework import status, exceptions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import APIException
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_decode_handler
from datetime import datetime
from django.core.mail import send_mail

from nilva1.settings import SECRET_KEY
from notification.serializers import UserSerializer
from .models import Notification


def authorization(request):
    token = request.headers['Authorization'].replace('Bearer ', '')
    try:
        payload = jwt_decode_handler(token)
        email = payload['email']
        user_id = payload['user_id']
        user = User.objects.get(
            email=email,
            id=user_id,
            is_active=True
        )
    except jwt.ExpiredSignature or jwt.DecodeError or jwt.InvalidTokenError:
        return HttpResponse({'Error': "Token is invalid"}, status="403")
    except User.DoesNotExist:
        return HttpResponse({'Error': "Internal server error"}, status="500")
    except Exception:
        return HttpResponse('Unauthorized!', status=401)

    return HttpResponse('* Available Access *')


def add_notif(request):
    dict_str = request.body.decode("UTF-8")
    body = ast.literal_eval(dict_str)
    new_notif = Notification(
        title=body['title'],
        description=body['description'],
        creator=body['creator'],
        relevant_staff=body['relevant_staff'],
        time_created=datetime.strptime(body['time_created'], '%d/%m/%y %H:%M:%S'),
        buffer_time=datetime.strptime(body['buffer_time'], '%d/%m/%y %H:%M:%S'),
        time_to_send = datetime.strptime(body['time_to_send'], '%d/%m/%y %H:%M:%S'),
        notification_types=body['notification_types'],
    )
    new_notif.save()
    return JsonResponse('Successful Operation', safe=False)


def edit_notif(request):
    dict_str = request.body.decode("UTF-8")
    body = ast.literal_eval(dict_str)
    try:
        editing_notif = Notification.objects.get(id=int(body['id']))
    except Exception:
        return HttpResponse('Invalid Notification ID!')
    if 'title' in body:
        editing_notif.title = body['title']
    if 'description' in body:
        editing_notif.description = body['description']
    if 'creator' in body:
        editing_notif.description = body['creator']
    if 'creator' in body:
        editing_notif.description = body['creator']
    if 'relevant_staff' in body:
        editing_notif.relevant_staff = body['relevant_staff']
    if 'time_created' in body:
        editing_notif.time_created = datetime.strptime(body['time_created'], '%d/%m/%y %H:%M:%S'),
    if 'buffer_time' in body:
        editing_notif.time_created = datetime.strptime(body['buffer_time'], '%d/%m/%y %H:%M:%S'),
    if 'time_to_send' in body:
        editing_notif.time_created = datetime.strptime(body['time_to_send'], '%d/%m/%y %H:%M:%S'),
    if 'notification_types' in body:
        editing_notif.notification_types = body['notification_types']

    editing_notif.save()
    return HttpResponse('Successful Operation')


def delete_notif(request):
    dict_str = request.body.decode("UTF-8")
    body = ast.literal_eval(dict_str)
    try:
        deleing_notif = Notification.objects.get(id=int(body['id']))
    except Exception:
        return HttpResponse('Invalid Notification ID!')
    deleing_notif.delete()
    return HttpResponse('Successful Operation')


def email_notif(request):
    dict_str = request.body.decode("UTF-8")
    body = ast.literal_eval(dict_str)
    title = body['title']
    content = body['content']
    from_mail = body['from_mail']
    to_mail = body['to_mail']
    send_mail(title, content, from_mail, to_mail, fail_silently=False)
    return HttpResponse('Successful Operation')


def SMS_notif(request):
    dict_str = request.body.decode("UTF-8")
    body = ast.literal_eval(dict_str)
    receptor = body['receptor']
    message = body['message']
    try:
        api = KavenegarAPI(
            '51474735396C536947576930554D724332327075506E78667532482B58462B71672B5A7148554E753939733D',
        )
        params = {
            # 'sender': '1000596446',# optional
            'receptor': receptor,# multiple mobile number, split by comma
            'message': message,
        }
        response = api.sms_send(params)
        print(response)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)


class CreateUserAPIView(APIView):
    # Allow any user (authenticated or not) to access this url
    permission_classes = (AllowAny,)

    def post(self, request):
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def authenticate_user(request):
    try:
        email = request.data['email']
        password = request.data['password']

        user = User.objects.get(email=email, password=password)
        if user:
            try:
                payload = jwt_payload_handler(user)
                token = jwt.encode(payload, SECRET_KEY)
                user_details = {'name': "%s %s" % (user.first_name, user.last_name), 'token': token}
                user_logged_in.send(sender=user.__class__, request=request, user=user)
                return Response(user_details, status=status.HTTP_200_OK)

            except Exception as e:
                raise e
        else:
            res = {
                'error': 'can not authenticate with the given credentials or the account has been deactivated'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
    except KeyError:
        res = {'error': 'please provide a email and a password'}
        return Response(res)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    # Allow only authenticated users to access this url
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        serializer = UserSerializer(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
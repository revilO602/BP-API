from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import connection
from django.http import JsonResponse
from account.api.serializers import RegistrationSerializer


# Respond with json of uptime
@api_view(['GET', ])
def uptime(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT date_trunc('second', current_timestamp - pg_postmaster_start_time()) as uptime;")
        row = cursor.fetchone()
    uptime = str(row[0])
    uptime = uptime.replace(',', '')
    return JsonResponse({"psql": {"uptime": uptime}})


# Register a new user
@api_view(['POST', ])
def registration_view(request):
    serializer = RegistrationSerializer(data=request.data)
    data = {}
    res_status = status.HTTP_400_BAD_REQUEST
    if serializer.is_valid():
        account = serializer.save()
        data['response'] = 'Successfully registered a new user account.'
        data['email'] = account.email
        data['first_name'] = account.first_name
        data['last_name'] = account.last_name
        data['phone_number'] = account.phone_number
        res_status = status.HTTP_201_CREATED
    else:
        data = serializer.errors
    return Response(data, status=res_status)


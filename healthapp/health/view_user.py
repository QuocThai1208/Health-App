from rest_framework.response import Response
from rest_framework import viewsets, generics, status, permissions
from . import serializers
from rest_framework.decorators import action
from .models import User, UserSchedule, Menu
from .google_fit import get_google_fit_water_intake, get_google_fit_steps, get_google_fit_heart_rate

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer

    @action(methods=['get', 'patch'], url_path="current-user", detail=False, permission_classes = [permissions.IsAuthenticated])
    def get_current_user(self, request):
        if request.method.__eq__('PATCH'):
            u = request.user

            for key in request.data:
                if key in ['first_name', 'last_name']:
                    setattr(u, key, request.data[key])
                elif key.__eq__('password'):
                    u.set_password(request.data[key])
            u.save()
            return Response(serializers.UserSerializer(u).data)
        else:
            return Response(serializers.UserSerializer(request.user).data)

    @action(methods=['get'], url_path='current-user/health-data', detail=False)
    def get_health_data_current_user(self,request):
        access_token = request.GET.get("access_token")
        if not access_token:
            return Response({"error": "Access token is missing"})
        return Response({ 'steps' : get_google_fit_steps(access_token),
                               'heart_rate()' : get_google_fit_heart_rate(access_token),
                               'water_inTake(Lit)' : get_google_fit_water_intake(access_token)}, status=status.HTTP_200_OK)

    @action(methods=['get', 'post', 'delete'], detail=False, url_path='current-user/schedule', permission_classes=[permissions.IsAuthenticated])
    def get_schedule(self, request):
        if request.method.__eq__('POST'):
            us = serializers.UserScheduleSerializer(data={
                'user' : request.user.id,
                'schedule': request.data.get('schedule')
            })
            us.is_valid()
            h = us.save()
            UserSchedule.objects.filter(user=request.user.id).exclude(schedule=request.data.get('schedule')).update(flag=False)
            return Response(serializers.UserScheduleSerializer(h).data, status=status.HTTP_200_OK)

        elif request.method.__eq__('DELETE'):
            UserSchedule.objects.filter(user=request.user.id,schedule=request.data.get('schedule')).delete()
            record = UserSchedule.objects.filter(user=request.user.id).first()
            if record:
                record.flag =True
                record.save()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        else:
            schedules = request.user.userschedule_set.filter(active=True)
            return Response(serializers.UserScheduleSerializer(schedules, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['post'], url_path='current-user/menu', detail=False)
    def post_schedule(self, request):
        u = request.user
        u.menu = Menu.objects.get(id=request.data.get('menu'))
        u.save()
        return Response(serializers.UserSerializer(u).data, status=status.HTTP_200_OK)
from datetime import timedelta

from django.db.models.functions import TruncDate
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import viewsets, generics, status, permissions
from django.db.models import Sum, F
from django.db import transaction
from django.utils import timezone
from . import serializers, perms
from rest_framework.decorators import action, permission_classes
from .models import User, HealthGoal, Schedule, GroupSchedule, Session, Exercise, ActualResult, PredictedResult, \
    UserSchedule, Diet, Menu, MenuOfDay, Ingredient, ResultOfSession, Reminder, HealthDiary, HealthInformation

from .google_fit import get_google_fit_water_intake, get_google_fit_steps, get_google_fit_heart_rate
from django.shortcuts import redirect
from django.conf import settings
import requests

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


class HealthInfoViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.UpdateAPIView):
    serializer_class = serializers.HealthInfoSerializer
    permission_classes = [perms.IsHealthInfoOwner]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return HealthInformation.objects.filter(user=self.request.user, active=True)




class GroupScheduleSViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = GroupSchedule.objects.filter(active=True)
    serializer_class = serializers.GroupScheduleSerializer

    @action(methods=['get'], url_path='schedule', detail=True)
    def get_schedule(self, request, pk):
        schedules = self.get_object().schedule_set.filter(active=True)
        return Response(serializers.ScheduleSerializer(schedules, many=True).data, status=status.HTTP_200_OK)


class ScheduleViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Schedule.objects.prefetch_related('Tags').filter(active=True)
    serializer_class = serializers.ScheduleDetailSerializer

    @action(methods=['get'], detail=True, url_path='session')
    def get_session(self, request, pk):
        sessions = self.get_object().session_set.prefetch_related('exercise').filter(active=True)
        return Response(serializers.SessionSerializer(sessions, many=True).data, status=status.HTTP_200_OK)


class SessionViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Session.objects.prefetch_related('exercise').filter(active=True)
    serializer_class = serializers.SessionDetailSerializer

    @action(methods=['get'], url_path='result', detail=True)
    def get_result(self, request, pk):
        results = self.get_object().resultofsession_set.filter(active=True)
        return Response(serializers.ResultOfSessionSerializer(results, many=True).data, status=status.HTTP_200_OK)


class ExerciseViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Exercise.objects.prefetch_related('tag').filter(active=True)
    serializer_class = serializers.ExerciseDetailSerializer

    @action(methods=['get'], url_path='actual-result', detail=True)
    def get_actual_result(self, request, pk):
        actual_result = self.get_object().actualresult_set.filter(active=True)
        return Response(serializers.ActualResultSerializer(actual_result, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='predicted-result', detail=True)
    def get_predicted_result(self, request, pk):
        predicted_result = self.get_object().predictedresult_set.filter(active=True)
        return Response(serializers.ActualResultSerializer(predicted_result, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='instruct', detail=True)
    def get_predicted_result(self, request, pk):
        instruct = self.get_object().instruct_set.filter(active=True)
        return Response(serializers.InstructSerializer(instruct, many=True).data, status=status.HTTP_200_OK)


class ActualResultViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = ActualResult.objects.filter(active=True)
    serializer_class = serializers.ActualResultSerializer


class PredictedResultViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = PredictedResult.objects.filter(active=True)
    serializer_class = serializers.PredictedResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        #nếu trong quá trình tạo 1 trong 2 bị lỗi quá trình tạo sẽ bị hủy bỏ
        with transaction.atomic():
            #lưu đối tượng vừa được tạo
            predicted_result = serializer.save(user=self.request.user)

            result_session = ResultOfSession.objects.filter(
                session=predicted_result.session,
                user=predicted_result.user,
                created_date__date=predicted_result.created_date
            ).first()

            if result_session is None:
                result_session = ResultOfSession.objects.create(
                    session = predicted_result.session,
                    user = predicted_result.user,
                    created_date = predicted_result.created_date,
                    practice_time= timedelta(seconds=0),
                    calo=0
                )
            result_session.calo += (0.1*predicted_result.weight*predicted_result.rep*predicted_result.set)
            result_session.save()

            health_diary = HealthDiary.objects.filter(
                user = predicted_result.user,
                created_date__date = predicted_result.created_date
            ).first()
            if health_diary is None:
                health_diary= HealthDiary.objects.create(
                    user = predicted_result.user,
                    calo_burned = result_session.calo,
                    calo_intake= 0,
                    weight = 0
                )
            health_diary.calo_burned = result_session.calo
            health_diary.save()


class DietViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Diet.objects.filter(active=True)
    serializer_class = serializers.DietSerializer

    @action(methods=['get'], url_path='menu', detail=True)
    def get_menu(self, request, pk):
        menus = self.get_object().menu_set.filter(active=True)
        return Response(serializers.MenuSerializer(menus, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='eating-method', detail=True)
    def get_eating_method(self, request, pk):
        eating_method = self.get_object().eatingmethod
        return Response(serializers.EatingMethodSerializer(eating_method).data, status=status.HTTP_200_OK)


class MenuViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Menu.objects.filter(active=True)
    serializer_class = serializers.MenuSerializer

    @action(methods=['get'], url_path='menu-of-day', detail=True)
    def get_menu_of_day(self, request, pk):
        menu_of_days = self.get_object().menuofday_set.filter(active=True)
        return Response(serializers.MenuOfDaySerializer(menu_of_days, many=True).data, status=status.HTTP_200_OK)


class MenuOfDayViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = MenuOfDay.objects.filter(active=True)
    serializer_class = serializers.MenuOfDayDetailSerializer

    @action(methods=['get'], url_path='meal', detail=True)
    def get_menu_of_day(self, request, pk):
        meals = self.get_object().meal_set.filter(active=True)
        return Response(serializers.MealSerializer(meals, many=True).data, status=status.HTTP_200_OK)


class IngredientViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Ingredient.objects.filter(active=True)
    serializer_class = serializers.IngredientDetailSerializer

    @action(methods=['get'], detail=True, url_path='nutrients')
    def get_nutrients(self, request, pk):
        nutrients = self.get_object().nutrients
        return Response(serializers.NutrientsSerializer(nutrients).data, status=status.HTTP_200_OK)


class StatsViewSet(viewsets.ViewSet):
    @action(methods=['get'], detail=False, permission_classes= [permissions.IsAuthenticated])
    def get(self, request):
        stats = PredictedResult.objects.filter(user_id=request.user.id, session_id=request.data.get('session')).aggregate(
            total_reps=Sum('rep'),
            total_sets=Sum('set'),
            total_weight=Sum(F('weight')*F('rep')*F('set'))
        )
        return Response(stats)

    @action(methods=['get'], detail=False, permission_classes= [permissions.IsAuthenticated])
    def get_practice_time(self, request):
        total_practice_time = ResultOfSession.objects.filter(user_id=request.user.id, session_id=request.data.get('session')).annotate(created_day = TruncDate('created_date')).values('created_day').annotate(total_practice_time=Sum('practice_time'))
        formatted_result=[
            {
                'date': entry['created_day'],
                ' total_practice_time': str(entry['total_practice_time'])
            }
            for entry in total_practice_time
        ]
        return Response(formatted_result, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, permission_classes= [permissions.IsAuthenticated])
    def get_calo(self, request):
        calo = ResultOfSession.objects.filter(user_id=request.user.id, session_id=request.data.get('session')).annotate(created_day = TruncDate('created_date')).values('created_day').annotate(calo=Sum('calo'))
        formatted_result=[
            {
                'date': entry['created_day'],
                ' calo': str(entry['calo'])
            }
            for entry in calo
        ]
        return Response(formatted_result, status=status.HTTP_200_OK)


class ReminderViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView , generics.DestroyAPIView, generics.UpdateAPIView):
    serializer_class = serializers.ReminderSerializer
    permission_classes = [perms.IsReminderOwner]

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user,active=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class HealthDiaryViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    serializer_class = serializers.HealthDiarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        today = timezone.now().date()
        health_diary = HealthDiary.objects.filter(
            user = self.request.user,
            created_date__date = today,
        ).first()

        if health_diary:
            health_diary.weight = self.request.data.get('weight', health_diary.weight)
            ingredient_ids = self.request.data.get('ingredient', [])
            if ingredient_ids:
                health_diary.ingredient.set(ingredient_ids)

            health_diary.save()
            serializer.instance = health_diary
        else:
            serializer.save(user=self.request.user)

    def get_queryset(self):
        return  HealthDiary.objects.filter(user=self.request.user, active=True)


# hàm khởi động quá trình xác thực oauth2 và chuyển hướng sáng trang đăng nhập
def google_fit_login(request):
    auth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        "?response_type=code"
        f"&client_id={settings.GOOGLE_FIT_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_FIT_REDIRECT_URI}"
        f"&scope={settings.GOOGLE_FIT_SCOPE}"
        "&access_type=offline"  # nhận refresh_token
        "&prompt=consent"  # Buộc Google hiển thị màn hình xác nhận quyền
    )
    return redirect(auth_url)


#hàm dùng để xác thực người dùng
def google_fit_callback(request):
    #lấy authorization code sau khi người dùng cấp quyền thông qua tham số code trong url
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "Missing authorization code"}, status=400)
    #gửi yêu cầu đến token_url để lấy token
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": settings.GOOGLE_FIT_CLIENT_ID,
        "client_secret": settings.GOOGLE_FIT_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.GOOGLE_FIT_REDIRECT_URI,
    }

    response = requests.post(token_url, data=data)
    tokens = response.json()

    if "access_token" not in tokens:
        return JsonResponse({"error": "Failed to obtain access token", "details": tokens}, status=400)

    access_token = tokens.get("access_token")

    # chuyển hướng
    return redirect(f"/users/current-user/health-data/?access_token={access_token}")



from rest_framework.response import Response
from rest_framework import viewsets, generics, status
from . import serializers, perms, paginators
from rest_framework.decorators import action
from .models import Tag, Schedule, GroupSchedule, Session, ActualResult, Diet, Menu, MenuOfDay, Ingredient, Reminder, HealthInformation


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

    @action(methods=['get'], url_path='schedules', detail=True)
    def get_schedule(self, request, pk):
        tag_ids = self.request.query_params.get('tag_ids')
        if tag_ids:
            schedules = self.get_object().schedule_set.filter(active=True, Tags__in=tag_ids)
        else:
            schedules = self.get_object().schedule_set.filter(active=True)
        return Response(serializers.ScheduleSerializer(schedules, many=True).data, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Tag.objects.filter(active=True)
    serializer_class = serializers.TagSerializer


class ScheduleViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Schedule.objects.prefetch_related('Tags').filter(active=True)
    serializer_class = serializers.ScheduleDetailSerializer
    pagination_class = paginators.ItemPaginator

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


class ActualResultViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = ActualResult.objects.filter(active=True)
    serializer_class = serializers.ActualResultSerializer


class DietViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Diet.objects.filter(active=True)
    serializer_class = serializers.DietSerializer
    pagination_class = paginators.ItemPaginator

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
    pagination_class = paginators.ItemPaginator

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
    pagination_class = paginators.ItemPaginator

    @action(methods=['get'], detail=True, url_path='nutrients')
    def get_nutrients(self, request, pk):
        nutrients = self.get_object().nutrients
        return Response(serializers.NutrientsSerializer(nutrients).data, status=status.HTTP_200_OK)


class ReminderViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView , generics.DestroyAPIView, generics.UpdateAPIView):
    serializer_class = serializers.ReminderSerializer
    permission_classes = [perms.IsReminderOwner]
    pagination_class = paginators.ItemPaginator

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user,active=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
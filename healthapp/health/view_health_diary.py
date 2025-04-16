from rest_framework import viewsets, generics, permissions
from django.utils import timezone
from . import serializers
from .models import  HealthDiary


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
            health_diary.height = self.request.data.get('height', health_diary.height)
            ingredient_ids = self.request.data.get('ingredient', [])
            if ingredient_ids:
                health_diary.ingredient.set(ingredient_ids)

            health_diary.save()
            serializer.instance = health_diary
        else:
            serializer.save(user=self.request.user)

    def get_queryset(self):
        return  HealthDiary.objects.filter(user=self.request.user, active=True)
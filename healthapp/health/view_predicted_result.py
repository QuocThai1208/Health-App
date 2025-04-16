from datetime import timedelta
from rest_framework import viewsets, generics, permissions
from django.db import transaction
from . import serializers
from .models import PredictedResult, ResultOfSession, HealthDiary


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
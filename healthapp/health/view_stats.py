from datetime import timedelta, date

from django.db.models.functions import TruncDate, TruncMonth
from rest_framework.response import Response
from rest_framework import viewsets, status, permissions
from django.db.models import Sum, F, Avg
from django.utils import timezone

from rest_framework.decorators import action
from .models import PredictedResult, ResultOfSession, HealthDiary


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

    @action(methods=['get'], detail=False, url_path='health-progress')
    def get_health_progress(self, request):
        today = timezone.now().date()
        month = request.query_params.get('month', None)
        year = request.query_params.get('year', None)

        if month and year:
            #tính ngày đầu tiên và ngày cuối cùng của tháng
            start_of_month = date(int(year), int(month), 1)
            end_of_month = start_of_month.replace(month = int(month) % 12 +1, day=1) - timedelta(days=1)

            #truy vấn dữ liệu trong khoản thời gian trên
            data = HealthDiary.objects.filter(user_id=request.user.id, created_date__range=(start_of_month, end_of_month)).annotate(created_day = TruncDate('created_date')).values('created_day', 'weight', 'height', 'bmi')

            #tính trung bình cho mỗi tuần
            week_data = []
            week_index = 1
            current_start = start_of_month
            while current_start <= end_of_month:

                current_end = current_start + timedelta(days=6)
                if current_end > end_of_month:
                    current_end = end_of_month

                #lấy dữ liệu của tuần đó
                week_entries = [entry for entry in data if current_start <= entry['created_day'] <= current_end]

                #tính giá trị trung bình các chỉ số
                week_weight = sum(entry['weight'] for entry in week_entries) / len(week_entries) if week_entries else None
                week_height = sum(entry['height'] for entry in week_entries) / len(week_entries) if week_entries else None
                week_bmi = sum(entry['bmi'] for entry in week_entries) / len(week_entries) if week_entries else None

                week_data.append({
                    'week': week_index,
                    'day_start': current_start,
                    'day_end': current_end,
                    'avg_weight': week_weight,
                    'avg_height': week_height,
                    'avg_bmi': week_bmi,
                })
                week_index+=1

                #lấy ngày đầu của tuần kế tiếp
                current_start = current_end + timedelta(days=1)

            return Response(week_data, status=status.HTTP_200_OK)
        if year:
            start_of_year = date(int(year), 1, 1)
            end_of_year = date(int(year), 12, 31)

            data = HealthDiary.objects.filter(user_id=request.user.id, created_date__range=(start_of_year, end_of_year)).annotate(month = TruncMonth('created_date')).values('month').annotate(
                avg_weight = Avg('weight'),
                avg_height = Avg('height'),
                avg_bmi = Avg('bmi'),
            )
            result =[]
            for entry in data:
                result.append({
                    'month': entry['month'].strftime('%B'),
                    'avg_weight': round(entry['avg_weight'], 2) if entry['avg_weight'] else None,
                    'avg_height': round(entry['avg_height'], 2) if entry['avg_height'] else None,
                    'avg_bmi': round(entry['avg_bmi'], 2) if entry['avg_bmi'] else None,
                })
            return Response(result, status=status.HTTP_200_OK)
        else:
            #today.weekday trả về 0 nếu là thứ 2
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)

            data = HealthDiary.objects.filter(user_id=request.user.id, created_date__range=(start_of_week, end_of_week)).annotate(created_day = TruncDate('created_date')).values('created_day', 'weight', 'height', 'bmi')

            data_dict = {entry['created_day']: {
                'weight': entry['weight'],
                'height': entry['height'],
                'bmi': entry['bmi'],
            }for entry in data}

            week_data = []
            for i in range(7):
                current_day = start_of_week + timedelta(days=i)
                info = data_dict.get(current_day, {})
                week_data.append({
                    #trả về tên của thứ
                    'day': current_day.strftime("%A"),
                    'date': current_day.isoformat(),
                    'weight': info.get('weight', None),
                    'height': info.get('height', None),
                    'bmi': info.get('bmi', None)
                })
            return Response(week_data, status=status.HTTP_200_OK)
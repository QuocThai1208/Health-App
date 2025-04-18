from django.urls import path, include
from . import views, view_stats, view_user, view_predicted_result, view_health_diary, view_exercise
from rest_framework.routers import DefaultRouter
from .view_google_fit import google_fit_login, google_fit_callback

router = DefaultRouter()
router.register('users', view_user.UserViewSet, basename='user')
router.register('group-schedules', views.GroupScheduleSViewSet, basename='group-schedule')
router.register('schedules', views.ScheduleViewSet, basename='schedule')
router.register('sessions', views.SessionViewSet, basename='session')
router.register('exercises', view_exercise.ExerciseViewSet, basename='exercise')
router.register('actual-result', views.ActualResultViewSet, basename='actual')
router.register('predicted-result', view_predicted_result.PredictedResultViewSet, basename='predicted')
router.register('diets', views.DietViewSet, basename='diet')
router.register('menus', views.MenuViewSet, basename='menu')
router.register('menu-of-days', views.MenuOfDayViewSet, basename='menu-of-day')
router.register('ingredient', views.IngredientViewSet, basename='ingredient')
router.register('stats', view_stats.StatsViewSet, basename='stats')
router.register('reminders', views.ReminderViewSet, basename='reminder')
router.register('health-diarys', view_health_diary.HealthDiaryViewSet, basename='health-diary')
router.register('health-info', views.HealthInfoViewSet, basename='health-info')
router.register('tags', views.TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls)),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path("login/google-fit/", google_fit_login, name="google_fit_login"),
    path("callback/google-fit/", google_fit_callback, name="google_fit_callback"),
]

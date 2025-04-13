from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import google_fit_login, google_fit_callback

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='user')
router.register('group-schedules', views.GroupScheduleSViewSet, basename='group-schedule')
router.register('schedules', views.ScheduleViewSet, basename='schedule')
router.register('sessions', views.SessionViewSet, basename='session')
router.register('exercises', views.ExerciseViewSet, basename='exercise')
router.register('actual-result', views.ActualResultViewSet, basename='actual')
router.register('predicted-result', views.PredictedResultViewSet, basename='predicted')
router.register('diets', views.DietViewSet, basename='diet')
router.register('menus', views.MenuViewSet, basename='menu')
router.register('menu-of-days', views.MenuOfDayViewSet, basename='menu-of-day')
router.register('ingredient', views.IngredientViewSet, basename='ingredient')
router.register('stats', views.StatsViewSet, basename='stats')
router.register('reminders', views.ReminderViewSet, basename='reminder')
router.register('health-diarys', views.HealthDiaryViewSet, basename='health-diary')
router.register('health-info', views.HealthInfoViewSet, basename='health-info')

urlpatterns = [
    path('', include(router.urls)),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path("login/google-fit/", google_fit_login, name="google_fit_login"),
    path("callback/google-fit/", google_fit_callback, name="google_fit_callback"),
]

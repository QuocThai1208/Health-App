from .models import User, HealthInformation, HealthGoal, Schedule, Tag, GroupSchedule, Exercise, Session, ActualResult, \
    PredictedResult, ResultOfSession, Instruct, UserSchedule, Diet, Menu, EatingMethod, MenuOfDay, Ingredient, \
    Nutrients, Dish, Meal, Reminder, HealthDiary

from rest_framework import serializers



class HealthGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthGoal
        fields = ['id', 'name']


class HealthInfoSerializer(serializers.ModelSerializer):
    # health_goal = HealthGoalSerializer()
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['health_goal'] = HealthGoalSerializer(instance.health_goal).data

        return data
    class Meta:
        model = HealthInformation
        fields = ['height', 'weight', 'age', 'health_goal']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']


class GroupScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupSchedule
        fields = ['name']


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'name',]


class ScheduleDetailSerializer(ScheduleSerializer):
    Tags = TagSerializer(many=True)
    class Meta:
        model = ScheduleSerializer.Meta.model
        fields = ScheduleSerializer.Meta.fields + ['Tags', 'total_day', 'describe']


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['id', 'name']


class ExerciseSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['image'] = instance.image.url if instance.image else ''
        return data

    class Meta:
        model = Exercise
        fields = ['name', 'image']


class ExerciseDetailSerializer(ExerciseSerializer):
    tag = TagSerializer(many=True)
    class Meta:
        model = ExerciseSerializer.Meta.model
        fields = ExerciseSerializer.Meta.fields + ['describe', 'tag']


class SessionDetailSerializer(SessionSerializer):
    exercise = ExerciseSerializer(many=True)
    class Meta:
        model = SessionSerializer.Meta.model
        fields = SessionSerializer.Meta.fields + ['exercise']

class ResultOfSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultOfSession
        fields = ['session', 'user', 'practice_time', 'calo']


class ActualResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActualResult
        fields = ['exercise', 'schedule', 'set', 'rep', 'weight']


class PredictedResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictedResult
        fields = ['exercise', 'session', 'user', 'set', 'rep', 'weight']


class InstructSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instruct
        fields = ['exercise', 'name', 'describe']


class UserScheduleSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['schedule'] = ScheduleSerializer(instance.schedule).data
        return data

    class Meta:
        model = UserSchedule
        fields = ['user', 'schedule', 'flag']


class DietSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diet
        fields = ['name', 'describe', 'image']


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['diet', 'name', 'total_day']


class MenuOfDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuOfDay
        fields = ['name']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['name']


class IngredientDetailSerializer(IngredientSerializer):
    class Meta:
        model = IngredientSerializer.Meta.model
        fields = IngredientSerializer.Meta.fields + ['unit', 'image']


class MenuOfDayDetailSerializer(MenuOfDaySerializer):
    ingredient = IngredientSerializer(many=True)
    class Meta:
        model = MenuOfDaySerializer.Meta.model
        fields = MenuOfDaySerializer.Meta.fields + ['id', 'ingredient']


class NutrientsSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()
    class Meta:
        model = Nutrients
        fields = ['ingredient', 'unit', 'kcal', 'fat', 'protein', 'starch']


class EatingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = EatingMethod
        fields = ['diet', 'introduce', 'principle', 'menu_building']


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ['name']


class MealSerializer(serializers.ModelSerializer):
    suggest_dish = DishSerializer(many=True)
    class Meta:
        model = Meal
        fields = ['name', 'suggest_dish']


class UserSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['avatar'] = instance.avatar.url if instance.avatar else ''
        data['menu'] = MenuSerializer(instance.menu).data if instance.menu else None
        return data

    def create(self, validated_data):
        data = validated_data.copy()
        u = User(**data)
        u.set_password(u.password)
        u.save()
        return u

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'address', 'password', 'avatar', 'user_role', 'menu']
        extra_kwargs = {
            'password':{
                'write_only':True
            }
        }


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ['id','reminder_type', 'reminder_time', 'message']


class HealthDiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthDiary
        fields =['calo_burned', 'ingredient', 'calo_intake', 'weight']
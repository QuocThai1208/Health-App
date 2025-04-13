from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField
from django.db.models import ForeignKey


class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-id']


class UserRole(models.IntegerChoices):
    ADMIN = 1, 'Admin'
    CUSTOMER = 2, 'Customer'
    NUTRITIONIST = 3, ' Nutritionist'
    COACH = 4, 'Coach'


class Message(BaseModel):
    content = models.CharField(max_length=255)

    def __str__(self):
        return self.content


class User(AbstractUser):
    address = models.CharField(max_length=255, null=True)
    avatar = CloudinaryField(null=True, blank=True)
    messages = models.ManyToManyField('Message', blank=True)
    menu = models.ForeignKey('Menu', null=True, blank=True, on_delete=models.SET_NULL)
    user_role = models.IntegerField(
        choices = UserRole.choices,
        default = UserRole.CUSTOMER
    )


class UserSchedule(BaseModel):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE)
    flag = models.BooleanField(default=True)



class HealthGoal(BaseModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class HealthInformation(BaseModel):
    user = models.OneToOneField('user', on_delete=models.CASCADE)
    health_goal = models.ForeignKey('HealthGoal', null=True, on_delete=models.SET_NULL, blank=True)
    height = models.FloatField()
    weight = models.FloatField()
    age = models.IntegerField()


class Tag(BaseModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class GroupSchedule(BaseModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Schedule(BaseModel):
    Tags = models.ManyToManyField('Tag')
    name = models.CharField(max_length=50)
    total_day = models.FloatField()
    describe = RichTextField()
    group_schedule = models.ForeignKey('GroupSchedule', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Session(BaseModel):
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    exercise = models.ManyToManyField('Exercise')

    def __str__(self):
        return self.name


class ResultOfSession(BaseModel):
    session = models.ForeignKey('Session', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE, default=1)
    practice_time = models.DurationField(default=timedelta(seconds=0))
    calo = models.IntegerField(null=True)
    workout_notes = models.CharField(max_length=255, default="")


class Result(BaseModel):
    rep = models.IntegerField(null=True)
    weight = models.FloatField(null=True)
    set = models.IntegerField(null=True)

    class Meta:
        abstract = True


class Exercise(BaseModel):
    name  = models.CharField(max_length=255)
    describe = models.CharField(max_length=255)
    image = CloudinaryField(null=True, blank=True)
    tag = models.ManyToManyField('Tag')
    def __str__(self):
        return self.name


class ActualResult(Result):
    exercise = models.ForeignKey('Exercise', on_delete=models.CASCADE)
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE, default=1)


class PredictedResult(Result):
    exercise = models.ForeignKey('Exercise', on_delete=models.CASCADE)
    session = models.ForeignKey('Session', on_delete=models.CASCADE)
    user = models.ForeignKey('user', on_delete=models.CASCADE, blank=True, null=True)
    # practice_time = models.DurationField()
    # restTime = models.DurationField()


class Instruct(BaseModel):
    exercise = models.ForeignKey('Exercise', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    describe = models.CharField(max_length=255)


class Diet(BaseModel):
    name = models.CharField(max_length=50)
    describe = models.CharField(max_length=255)
    image = CloudinaryField(null=True, blank=True)

    def __str__(self):
        return self.name

class Menu(BaseModel):
    diet = models.ForeignKey('Diet', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    total_day = models.IntegerField()

    def __str__(self):
        return self.name

class EatingMethod(BaseModel):
    diet = models.OneToOneField('Diet', on_delete=models.CASCADE)
    introduce = RichTextField()
    principle = RichTextField()
    menu_building = RichTextField()


class MenuOfDay(BaseModel):
    menu = models.ForeignKey('Menu', on_delete=models.CASCADE)
    ingredient = models.ManyToManyField('Ingredient')
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Dish(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Meal(BaseModel):
    menu_of_day = models.ForeignKey('MenuOfDay', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    suggest_dish = models.ManyToManyField('Dish')


class Nutrients(BaseModel):
    ingredient = models.OneToOneField('Ingredient', on_delete=models.CASCADE, null=True)
    unit = models.IntegerField(default=1)
    kcal = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    protein = models.FloatField(default=0)
    starch = models.FloatField(default=0)



class Ingredient(BaseModel):
    name = models.CharField(max_length=50)
    unit = models.CharField(max_length=50)
    image = CloudinaryField(null=True, blank=True)

    def __str__(self):
        return self.name


class Reminder(BaseModel):
    REMINDER_TYPES=[
        ('water', 'Uống nước'),
        ('exercise', 'Tập luyện'),
        ('rest', 'Nghỉ ngơi')
    ]

    user = models.ForeignKey('User', on_delete=models.CASCADE)
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES)
    reminder_time = models.TimeField()
    message = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"{self.get_reminder_type_display()} - {self.reminder_time}"


class HealthDiary(BaseModel):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    calo_burned = models.IntegerField(default=0)
    calo_intake = models.IntegerField(default=0)
    ingredient = models.ManyToManyField('Ingredient', null=True, blank=True)
    weight = models.FloatField(default=0)

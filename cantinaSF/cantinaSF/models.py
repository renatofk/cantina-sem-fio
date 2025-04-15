from django.db import models
from django.contrib.auth import get_user_model

from wagtail.models import Page, Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel
from wagtail.images.models import Image

User = get_user_model()

class Course(models.Model):
    course_name = models.CharField(max_length=200)
    teacher = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.course_name} - {self.teacher}'
    
class Meal(models.Model):
    meal_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f'{self.meal_name} - {self.price} R$'


class Student(ClusterableModel):
    PLAN_CHOICES = [
        ('assinatura', 'Assinatura'),
        ('avulso', 'Avulso'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    birthday = models.DateField()
    creation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    courses = models.ManyToManyField(Course, blank=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('last_name'),
        FieldPanel('plan'),
        FieldPanel('birthday'),
        FieldPanel('status'),
        FieldPanel('user'),
        FieldPanel('courses'),
        InlinePanel('photos', label="Photos"),
    ]

    def __str__(self):
        return f'{self.name} {self.last_name}'


class StudentPhoto(Orderable):
    student = ParentalKey(Student, on_delete=models.CASCADE, related_name='photos')
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('image')  # onde "image" é o campo ForeignKey para Image
    ]

class History(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='histories')
    meal = models.ForeignKey('Meal', on_delete=models.SET_NULL, null=True, related_name='histories')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.student.name} - {self.meal.meal_name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

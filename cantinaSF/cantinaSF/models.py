from django.db import models
from django.contrib.auth import get_user_model

from wagtail.models import Page, Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel, HelpPanel
from wagtail.fields import RichTextField
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Course(models.Model):
    course_name = models.CharField(max_length=200)
    teacher = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")

    def __str__(self):
        return f'{self.course_name} - {self.teacher}'
    
class Meal(models.Model):
    meal_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        verbose_name = _("Meal")
        verbose_name_plural = _("Meals")

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

    name = models.CharField(_('Name'), max_length=100)
    last_name = models.CharField(_('Sobrenome'), max_length=100)
    plan = models.CharField(_('Plan'), max_length=20, choices=PLAN_CHOICES)
    birthday = models.DateField(_('Data de nascimento'), )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Responsable"))
    # courses = models.ManyToManyField(Course, blank=True, verbose_name=_("Curso"))
    courses = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Curso"))
    balance = models.DecimalField(_('Balance'), max_digits=8, decimal_places=2, default=0.00)
    creation_date = models.DateTimeField(_('Creation Date'), auto_now_add=True)

    class Meta:
        verbose_name = _("Student")
        verbose_name_plural = _("Students")

    panels = [
        FieldPanel("name"),
        FieldPanel("last_name"),
        FieldPanel("plan"),
        FieldPanel("birthday"),
        FieldPanel("status"),
        FieldPanel("user"),
        FieldPanel("courses"),
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
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='histories', verbose_name=_("Aluno"))
    meal = models.ForeignKey('Meal', on_delete=models.SET_NULL, null=True, related_name='histories', verbose_name=_("Refeição"))
    detected_at = models.DateTimeField(_('Detected At'), null=True, blank=True)
    approved_by = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("Aprovado por"))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _("History")
        verbose_name_plural = _("Histories")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.name} - {self.meal.meal_name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

# Transações que serão usadas para registrar os gastos dos alunos
class Transaction(models.Model):
    TYPES = [
        ('credito', 'Crédito'),
        ('debito', 'Débito'),
    ]
    history = models.ForeignKey(History, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Histórico"))
    valor = models.DecimalField(_('Value'), max_digits=8, decimal_places=2)
    username = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Responsável"))
    username.read_only = True
    type = models.CharField(_('Type'), max_length=10, choices=TYPES, default='debito')
    type.read_only = True
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.history} - R$ {self.valor:.2f} - {self.created_at:%d/%m/%Y %H:%M}"
    

from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.contrib.auth.models import Group

@receiver(user_signed_up)
def add_to_group(sender, request, user, **kwargs):
    group = Group.objects.get(id=3)
    user.groups.add(group)
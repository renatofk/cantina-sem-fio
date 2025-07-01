from django.db import models
from django.contrib.auth import get_user_model

from wagtail.models import Page, Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel, HelpPanel
from wagtail.fields import RichTextField
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel
from django.utils.html import format_html

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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    courses = models.ManyToManyField(Course, blank=True)
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    creation_date = models.DateTimeField(auto_now_add=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("last_name"),
        FieldPanel("plan"),
        FieldPanel("birthday"),
        FieldPanel("status"),
        FieldPanel("user"),
        FieldPanel("courses"),
        # HelpPanel(
        #     content=format_html(
        #         """
        #         <button type="button" class="button button-small button-secondary" onclick="openCaptureModal()">📷 Capturar Foto</button>
        #         <div id="captureModal" style="display:none; position:fixed; top:5%; left:5%; width:90%; height:90%; background:white; border:2px solid #ccc; z-index:10000;">
        #             <div style="padding:10px; text-align:right;">
        #                 <button onclick="closeCaptureModal()">Fechar</button>
        #             </div>
        #             <iframe id="captureFrame" src="" style="width:100%; height:90%; border:none;"></iframe>
        #         </div>

        #         <script>
        #             function openCaptureModal() {{
        #                 const nameField = document.querySelector('input[name="name"]');
        #                 const name = nameField ? nameField.value : '';

        #                 // Pega o ID da URL como /123/change/
        #                 const match = window.location.pathname.match(/(\\d+)/);
        #                 const id = match ? match[1] : '';

        #                 const modal = document.getElementById('captureModal');
        #                 const frame = document.getElementById('captureFrame');
        #                 frame.src = "http://127.0.0.1:5001/camera?student_id=" + id + "&student_name=" + encodeURIComponent(name);
        #                 modal.style.display = 'block';
        #             }}

        #             function closeCaptureModal() {{
        #                 document.getElementById('captureModal').style.display = 'none';
        #             }}
        #         </script>
        #         """
        #     ),
        #     heading="Captura de Foto",
        # ),
        # InlinePanel("photos", label="Fotos do aluno"),
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
    detected_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.meal.meal_name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

# Transações que serão usadas para registrar os gastos dos alunos
class Transaction(models.Model):
    TYPES = [
        ('credito', 'Crédito'),
        ('debito', 'Débito'),
    ]
    history = models.ForeignKey(History, on_delete=models.SET_NULL, null=True, blank=True)
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    username = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    username.read_only = True
    type = models.CharField(max_length=10, choices=TYPES, default='debito')
    type.read_only = True
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.history} - R$ {self.valor:.2f} - {self.created_at:%d/%m/%Y %H:%M}"
    

from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.contrib.auth.models import Group

@receiver(user_signed_up)
def add_to_group(sender, request, user, **kwargs):
    group = Group.objects.get(id=3)
    user.groups.add(group)
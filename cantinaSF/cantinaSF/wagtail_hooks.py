
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from .models import CaraPassaDevice, CaraPassaEvent, Student, Course, Meal, History, Transaction
# em wagtail_hooks.py
from django.utils.html import format_html
from django.templatetags.static import static
from wagtail import hooks                       

from django.urls import reverse
from django.utils.html import format_html
from wagtail import hooks
from wagtail_modeladmin.views import CreateView, DeleteView, EditView
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Q
from .forms import TransactionForm, StudentForm
from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from urllib.parse import urlencode
from .carapassa_client import CaraPassaSubjectDeletionError, delete_subject

@hooks.register('construct_main_menu')
def hide_default_wagtail_menu_items(request, menu_items):
    names_to_remove = {
        'search',
        'pages',
        'images',
        'documents',
    }
    labels_to_remove = {
        'Search',
        'Pages',
        'Images',
        'Documents',
        'Busca',
        'Páginas',
        'Imagens',
        'Documentos',
    }

    menu_items[:] = [
        item for item in menu_items
        if getattr(item, 'name', None) not in names_to_remove
        and getattr(item, 'label', None) not in labels_to_remove
    ]


@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static('css/custom-wagtail.css')
    )

@hooks.register('insert_global_admin_js')
def hide_help_menu_js():
    return format_html(
        '<script src="{}"></script><script src="{}"></script>',
        static('js/hide_help_menu.js'),
        static('js/carapassa_capture.js'),
    )

@hooks.register('insert_editor_js')
def editor_js():
    return format_html(
        '<script src="/static/js/birth_date_mask.js"></script>'
    )

class StudentCreateView(CreateView):
    def get_form_class(self):
        return StudentForm
    
    def get_form(self):
        form = super().get_form()

        # Deixar o campo `user` como readonly e desabilitado
        if 'user' in form.fields:
            form.fields['user'].widget.attrs['readonly'] = True
            form.fields['user'].widget.attrs['disabled'] = True
            form.fields['user'].required = False  # Evita erro de validação

        # Adicionar classe CSS para o campo birthday
        if 'birthday' in form.fields:
            form.fields['birthday'].widget.attrs['class'] = 'datepicker'

        return form
    
    def form_valid(self, form):
        form.instance.user = self.request.user # Grava o usuário atual
        return super().form_valid(form)
    
class StudentEditView(EditView):
    def get_form_class(self):
        return StudentForm
    
    def get_form(self):
        form = super().get_form()

        # Deixar o campo `user` como readonly e desabilitado
        if 'user' in form.fields:
            form.fields['user'].disabled = True
            form.fields['user'].required = False  # Evita erro de validação

        # Adicionar classe CSS para o campo birthday
        if 'birthday' in form.fields:
            form.fields['birthday'].widget.attrs['class'] = 'datepicker'

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'].for_user = self.request.user  # Pass the user to the form
        return context
    
    def form_valid(self, form):
        form.instance.user = self.instance.user # Mantém o usuário original
        return super().form_valid(form)


class StudentDeleteView(DeleteView):
    def delete_instance(self):
        delete_subject(self.instance.integration_id)
        super().delete_instance()

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except CaraPassaSubjectDeletionError as exc:
            messages.error(request, str(exc))
            return redirect(self.index_url)
    

class StudentAdmin(ModelAdmin):
    model = Student
    menu_label = _('Alunos')
    menu_icon = 'user'
    form_class = StudentForm
    list_display = ("__str__", "plan", "balance", "capture_button")
    search_fields = ('name', 'last_name')
    create_view_class = StudentCreateView
    edit_view_class = StudentEditView
    delete_view_class = StudentDeleteView

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(id=3).exists():
            return qs.filter(user=request.user)
        return qs

    def capture_button(self, obj):
        capture_url = f"{settings.CARAPASSA_APP_URL.rstrip('/')}/captura"
        button_label = "Verificando foto..."
        query = urlencode({
            "api_key": settings.CARAPASSA_API_KEY,
            "subject_id": str(obj.integration_id),
        })
        return format_html(
            '<a href="{}?{}" target="_blank" '
            'rel="noreferrer" class="button button-small js-carapassa-capture" '
            'data-subject-id="{}" data-status-url="{}" data-carapassa-origin="{}">{}</a>',
            capture_url, query,
            obj.integration_id,
            reverse("carapassa_face_status"),
            settings.CARAPASSA_APP_URL.rstrip('/'),
            button_label,
        )

    capture_button.short_description = "Captura"


class CourseAdmin(ModelAdmin):
    model = Course
    menu_label = 'Turmas'
    menu_icon = 'group'
    list_display = ('course_name', 'teacher')
    search_fields = ('course_name', 'teacher')


class MealAdmin(ModelAdmin):
    model = Meal
    menu_label = 'Refeições'
    menu_icon = 'time'
    list_display = ('meal_name', 'price', 'start_time', 'end_time')


class HistoryAdmin(ModelAdmin):
    model = History
    menu_label = 'Histórico'
    menu_icon = 'date'
    list_display = ('student', 'meal', 'created_at', 'approved_by')
    search_fields = ('student__name', 'meal__meal_name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(id=3).exists():
            return qs.filter(student__user=request.user)
        return qs  

class TransactionCreateView(CreateView):
    def get_form(self):
        form = super().get_form()

        if 'type' in form.base_fields:
            form.initial['type'] = 'credito'
            form.fields['type'].widget.attrs['readonly'] = True
            form.fields['type'].widget.attrs['disabled'] = True
            form.fields['type'].required = False  # evita erro de validação
            # form.fields['type'].widget = forms.HiddenInput()

        if 'username' in form.base_fields:
            form.initial['username'] = self.request.user
            form.fields['username'].widget.attrs['readonly'] = True
            form.fields['username'].widget.attrs['disabled'] = True
            form.fields['username'].required = False

        form.fields.pop('history', None)
        # form.fields.pop('type', None)
        # form.fields.pop('username', None)
        return form
    
    def form_valid(self, form):
        # Força os valores mesmo se vierem do frontend com outro valor
        form.instance.type = 'credito'
        form.instance.username = self.request.user

        response = super().form_valid(form)

        students = Student.objects.filter(user=self.request.user)
        for student in students:
            student.balance += form.instance.valor
            student.save()

        return response


class TransactionAdmin(ModelAdmin):
    model = Transaction
    menu_label = 'Transações'
    menu_icon = 'resubmit'
    list_display = ('history', 'username', 'valor', 'type', 'created_at')
    search_fields = ('history__student__name', 'username__username')
    form_class = TransactionForm
    create_view_class = TransactionCreateView

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Se o usuário pertence ao group_id = 3, mostrar apenas suas próprias transações
        if request.user.groups.filter(id=3).exists():
            qs = qs.filter(
                Q(username=request.user) |
                Q(history__student__user=request.user)
            )
        return qs


class CaraPassaDeviceAdmin(ModelAdmin):
    model = CaraPassaDevice
    menu_label = "Dispositivos CaraPassa"
    menu_icon = "site"
    list_display = ("name", "tenant_id", "school_id", "device_id", "active")
    search_fields = ("name", "tenant_id", "school_id", "device_id")


class CaraPassaEventAdmin(ModelAdmin):
    model = CaraPassaEvent
    menu_label = "Eventos CaraPassa"
    menu_icon = "view"
    list_display = ("event_id", "student", "device_mapping", "processing_status", "occurred_at")
    list_filter = ("processing_status",)
    search_fields = ("event_id", "subject_id", "device_id", "processing_error")
    inspect_view_enabled = True
    create_view_enabled = False
    edit_view_enabled = False
    delete_view_enabled = False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(id=3).exists():
            return qs.filter(student__user=request.user)
        return qs
    
class CustomParentHistoryPanel:
    order = 100

    def __init__(self, request):
        self.request = request

    def render_html(self, request):
        
        students = Student.objects.filter(user=self.request.user)
        histories = History.objects.filter(student__in=students).order_by('-created_at')[:10]  # Pega os 10 mais recentes
        saldo_total = 0
        for student in students:
            print(f"Saldo do aluno {student.name}: {student.balance}")
            if student.balance > saldo_total:
                saldo_total = student.balance
        
        return render_to_string("dashboard/parent_panel.html", {
            "histories": histories,
            "saldo_total": saldo_total
        })

    @property
    def media(self):
        from django.forms.widgets import Media
        return Media()


class CaraPassaRecognitionPanel:
    order = -100

    def __init__(self, request):
        self.request = request

    def render_html(self, parent_context):
        recognition_url = ""
        if settings.CARAPASSA_API_KEY:
            recognition_url = (
                f"{settings.CARAPASSA_APP_URL.rstrip('/')}"
                f"?{urlencode({'api_key': settings.CARAPASSA_API_KEY})}"
            )
        return render_to_string(
            "dashboard/carapassa_recognition_panel.html",
            {"recognition_url": recognition_url},
            request=self.request,
        )

    @property
    def media(self):
        from django.forms.widgets import Media
        return Media()


@hooks.register('construct_homepage_panels')
def add_custom_history_panel(request, panels):
    # Responsáveis não devem receber a chave do dispositivo de reconhecimento.
    if not request.user.groups.filter(id=3).exists():
        panels.insert(0, CaraPassaRecognitionPanel(request))
    panels.append(CustomParentHistoryPanel(request))

modeladmin_register(StudentAdmin)
modeladmin_register(CourseAdmin)
modeladmin_register(MealAdmin)
modeladmin_register(HistoryAdmin)
modeladmin_register(TransactionAdmin)
modeladmin_register(CaraPassaDeviceAdmin)
modeladmin_register(CaraPassaEventAdmin)

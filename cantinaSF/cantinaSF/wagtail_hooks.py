
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from .models import Student, Course, Meal, History, Transaction
# em wagtail_hooks.py
from django.utils.html import format_html
from django.templatetags.static import static
from wagtail import hooks                       

from django.urls import reverse
from django.utils.html import format_html
from wagtail import hooks
from wagtail_modeladmin.views import CreateView, EditView
from django.db.models import Q
from .forms import TransactionForm, StudentForm
from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _

@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static('css/custom-wagtail.css')
    )

@hooks.register('insert_global_admin_js')
def hide_help_menu_js():
    return format_html(
        '<script src="{}"></script>',
        static('js/hide_help_menu.js')
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
    
class StudentEditView(EditView):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'].for_user = self.request.user  # Pass the user to the form
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class StudentAdmin(ModelAdmin):
    model = Student
    menu_label = _('Alunos')
    menu_icon = 'user'
    form_class = StudentForm
    list_display = ("__str__", "plan", "balance", "capture_button")
    search_fields = ('name', 'last_name')
    create_view_class = StudentCreateView
    edit_view_class = StudentEditView

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(id=3).exists():
            return qs.filter(user=request.user)
        return qs

    def capture_button(self, obj):
        return format_html('''
            <form action="https://captura.cantinasemfila.com.br/camera" method="post" target="_blank" id="form_{0}">
                <input type="hidden" name="student_id" value="{0}" />
                <input type="hidden" name="student_name" value="{1}" />
                <button type="submit" class="button button-small">Capturar Foto</button>
            </form>
        ''', obj.id, obj.name)

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

@hooks.register('construct_homepage_panels')
def add_custom_history_panel(request, panels):
    panels.append(CustomParentHistoryPanel(request))

modeladmin_register(StudentAdmin)
modeladmin_register(CourseAdmin)
modeladmin_register(MealAdmin)
modeladmin_register(HistoryAdmin)
modeladmin_register(TransactionAdmin)



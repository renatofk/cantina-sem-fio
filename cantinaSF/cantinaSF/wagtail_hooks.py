
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from .models import Student, Course, Meal, History, Transaction
# em wagtail_hooks.py
from django.utils.html import format_html
from django.templatetags.static import static
from wagtail import hooks                       

from django.urls import reverse
from django.utils.html import format_html
from wagtail import hooks
from .models import Student

@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static('css/custom-wagtail.css')
    )

@hooks.register('insert_global_admin_js')
def global_admin_js():
    return format_html('<script src="{}"></script>', static('js/capture_modal.js'))

class StudentAdmin(ModelAdmin):
    model = Student
    menu_label = 'Alunos'
    menu_icon = 'user'
    list_display = ("__str__", "plan", "balance", "status", "capture_button")
    search_fields = ('name', 'last_name')



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

class TransactionAdmin(ModelAdmin):
    model = Transaction
    menu_label = 'Transações'
    menu_icon = 'resubmit'
    list_display = ('history', 'valor', 'username', 'created_at')
    search_fields = ('history__student__name', 'username__username')

modeladmin_register(StudentAdmin)
modeladmin_register(CourseAdmin)
modeladmin_register(MealAdmin)
modeladmin_register(HistoryAdmin)
modeladmin_register(TransactionAdmin)




from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from .models import Student, Course, Meal, History
# em wagtail_hooks.py
from django.utils.html import format_html
from django.templatetags.static import static
from wagtail import hooks                       

from django.urls import reverse
from django.utils.html import format_html
from wagtail import hooks
from .models import Student


@hooks.register("insert_editor_js")
def custom_admin_js():
    return format_html("""
        <script>
        function openCaptureModal(studentId) {{
            const modal = document.createElement('div');
            modal.style.position = 'fixed';
            modal.style.top = '0';
            modal.style.left = '0';
            modal.style.width = '100vw';
            modal.style.height = '100vh';
            modal.style.background = 'rgba(0, 0, 0, 0.8)';
            modal.style.zIndex = '9999';

            const iframe = document.createElement('iframe');
            iframe.src = `http://127.0.0.1:5006/student_id=${{studentId}}`;
            iframe.style.width = '90%';
            iframe.style.height = '90%';
            iframe.style.border = 'none';
            iframe.style.margin = '5%';
            iframe.style.borderRadius = '16px';
            iframe.style.background = '#fff';

            const closeBtn = document.createElement('button');
            closeBtn.innerText = 'Fechar';
            closeBtn.style.position = 'absolute';
            closeBtn.style.top = '20px';
            closeBtn.style.right = '30px';
            closeBtn.style.zIndex = '10000';
            closeBtn.style.padding = '10px 20px';
            closeBtn.style.background = '#fff';
            closeBtn.style.border = '1px solid #ccc';
            closeBtn.style.borderRadius = '8px';
            closeBtn.onclick = () => document.body.removeChild(modal);

            modal.appendChild(iframe);
            modal.appendChild(closeBtn);
            document.body.appendChild(modal);
        }}
        </script>
    """)

class StudentAdmin(ModelAdmin):
    model = Student
    menu_label = 'Alunos'
    menu_icon = 'user'
    list_display = ('name', 'last_name', 'plan', 'status')
    search_fields = ('name', 'last_name')


class CourseAdmin(ModelAdmin):
    model = Course
    menu_label = 'Cursos'
    menu_icon = 'group'
    list_display = ('course_name', 'teacher')
    search_fields = ('course_name', 'teacher')


class MealAdmin(ModelAdmin):
    model = Meal
    menu_label = 'Refeições'
    menu_icon = 'cup'
    list_display = ('meal_name', 'price', 'start_time', 'end_time')


class HistoryAdmin(ModelAdmin):
    model = History
    menu_label = 'Histórico'
    menu_icon = 'date'
    list_display = ('student', 'meal', 'created_at', 'approved_by')
    search_fields = ('student__name', 'meal__meal_name')


modeladmin_register(StudentAdmin)
modeladmin_register(CourseAdmin)
modeladmin_register(MealAdmin)
modeladmin_register(HistoryAdmin)




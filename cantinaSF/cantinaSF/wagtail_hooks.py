
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
    # list_display = ("__str__", "plan", "balance", "status", "capture_photo_button")
    list_display = ("__str__", "plan", "balance", "status", "capture_button")
    #list_display = ('name', 'last_name', 'plan', 'status')
    search_fields = ('name', 'last_name')

    # def capture_photo_button(self, obj):
    #     capture_url = reverse('capture_photo', kwargs={'student_id': obj.id, 'student_name': obj.name})
    #     return format_html(
    #         '''
    #         <button type="button" class="button button-small button-secondary" onclick="loadCaptureModal('{url}')">📷</button>
    #         ''',
    #         url=capture_url
    #     )
    # capture_photo_button.short_description = "Captura"

    # <form action="https://captura.cantinasemfila.com.br/camera" method="post" target="_blank" id="form_{0}">
    #             <input type="hidden" name="student_id" value="{0}" />
    #             <input type="hidden" name="student_name" value="{1}" />
    #             <button type="submit" class="button button-small">Capturar Foto</button>
    #         </form>

    def capture_button(self, obj):
        return format_html('''
            <button class="button button-small" onclick="openCaptureWindow({0}, '{1}')">Capturar</button>
            <style>
                .modal-overlay {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0,0,0,0.5);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 10000;
                }}
                .modal-content {{
                    background-color: white;
                    padding: 10px;
                    border-radius: 8px;
                    width: 80%;
                    height: 80%;
                    position: relative;
                }}
                .modal-content iframe {{
                    width: 100%;
                    height: 100%;
                    border: none;
                }}
                .modal-close {{
                    position: absolute;
                    top: 5px;
                    right: 10px;
                    background: red;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                    cursor: pointer;
                }}
            </style>
            <script>
            function openCaptureWindow(id, name) {{
                // Cria modal
                let existingOverlay = document.getElementById('modal-overlay');
                if (existingOverlay) {{
                    existingOverlay.remove(); // Remove se já existir
                }}

                const overlay = document.createElement('div');
                overlay.id = 'modal-overlay';
                overlay.className = 'modal-overlay';

                const modal = document.createElement('div');
                modal.className = 'modal-content';

                const closeBtn = document.createElement('button');
                closeBtn.className = 'modal-close';
                closeBtn.innerText = 'Fechar';
                closeBtn.onclick = () => document.body.removeChild(overlay);

                const iframe = document.createElement('iframe');
                iframe.name = 'captureFrame';
                iframe.id = 'captureFrame';
                iframe.setAttribute('allow', 'camera; microphone');

                modal.appendChild(closeBtn);
                modal.appendChild(iframe);
                overlay.appendChild(modal);
                document.body.appendChild(overlay);

                // Cria form e envia os dados
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = 'https://captura.cantinasemfila.com.br/camera';
                form.target = 'captureFrame';

                const input1 = document.createElement('input');
                input1.type = 'hidden';
                input1.name = 'student_id';
                input1.value = id;
                form.appendChild(input1);

                const input2 = document.createElement('input');
                input2.type = 'hidden';
                input2.name = 'student_name';
                input2.value = name;
                form.appendChild(input2);

                document.body.appendChild(form);
                form.submit();
                document.body.removeChild(form);
            }}
            </script>
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



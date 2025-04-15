# Em um arquivo chamado widgets.py no seu app
from django.forms.widgets import FileInput
from django.template.loader import render_to_string

class CameraEnabledFileInput(FileInput):
    template_name = 'widgets/camera_file_input.html'
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        return context
# # # admin.py
# from wagtail.admin.viewsets.model import ModelViewSet
# from wagtail import hooks
# from .models import Student, Course, Meal, History

# class StudentViewSet(ModelViewSet):
#     model = Student
#     menu_label = "Alunos"
#     menu_icon = "user"
#     add_to_admin_menu = True
#     list_display = ["name", "last_name", "plan", "status"]
#     search_fields = ["name", "last_name"]

# class CourseViewSet(ModelViewSet):
#     model = Course
#     menu_label = "Cursos"
#     menu_icon = "book"
#     add_to_admin_menu = True

# class MealViewSet(ModelViewSet):
#     model = Meal
#     menu_label = "Refeições"
#     menu_icon = "coffee"
#     add_to_admin_menu = True

# class HistoryViewSet(ModelViewSet):
#     model = History
#     menu_label = "Histórico"
#     menu_icon = "clock"
#     add_to_admin_menu = True

# @hooks.register("register_admin_viewset")
# def register_student_viewset():
#     return StudentViewSet()

# @hooks.register("register_admin_viewset")
# def register_course_viewset():
#     return CourseViewSet()

# @hooks.register("register_admin_viewset")
# def register_meal_viewset():
#     return MealViewSet()

# @hooks.register("register_admin_viewset")
# def register_history_viewset():
#     return HistoryViewSet()

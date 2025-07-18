from django.conf import settings
from django.urls import include, path, re_path
from django.shortcuts import redirect
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from .views import registrar_presencas
from . import views

from search import views as search_views

urlpatterns = [
    path('', lambda request: redirect('account_login')),
    path("django-admin/", admin.site.urls),
    re_path(r'^admin/login/$', lambda request: redirect('/accounts/login/')),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
    path("api/registrar-presencas/", registrar_presencas),
    path('capture_photo/<int:student_id>/<str:student_name>/', views.capture_photo_view, name='capture_photo'),
    path("accounts/", include("allauth.urls")),

]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]

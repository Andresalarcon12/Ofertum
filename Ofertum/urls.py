from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.views.generic.base import RedirectView

# Ruta para cambio de idioma y redirección raíz
urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("", RedirectView.as_view(url='/es/', permanent=False)),  # Redirigir raíz a español por defecto
]

# Rutas con soporte multiidioma (con prefijos /es/ y /en/)
urlpatterns += i18n_patterns(
    path("", include("catalog.urls")),
    path("admin/", admin.site.urls),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

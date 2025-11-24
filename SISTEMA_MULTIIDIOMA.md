# Sistema Multiidioma - Ofertum

## ✅ Implementación Completada

El sistema de internacionalización (i18n) está completamente configurado y funcional para **Español (ES)** e **Inglés (EN)**.

---

## 🌍 Características Implementadas

### 1. **Selector de Idioma en Navbar**
- Ubicación: Esquina superior derecha
- Selector con banderas: 🇪🇸 ES / 🇬🇧 EN
- Cambio automático al seleccionar
- Mantiene la página actual después del cambio
- Estilo integrado con el diseño del sitio

### 2. **Traducciones Completas**
Se han traducido **más de 100 cadenas de texto** incluyendo:

#### Navegación y UI General
- Menú principal (Productos, Categorías, Tiendas, Páginas Aliadas)
- Botones de acción (Buscar, Aplicar, Crear propuesta, etc.)
- Enlaces de autenticación (Login, Registro, Cerrar sesión)
- Selector de idioma

#### Lista de Productos
- Filtros (búsqueda, categoría, tienda, precio, rating)
- Ordenamiento (nombre, precio asc/desc, mejor valorados)
- Labels de formularios
- Chips de filtros activos
- Mensajes de estado
- Botones de exportación (PDF, Excel)
- Paginación

#### Productos y Detalles
- Estados de productos (disponible, oferta activa)
- Información de precios
- Ratings y reseñas
- Enlaces a tiendas

#### Páginas Aliadas
- Banner informativo
- Badge de "Producto aliado"
- Mensajes de error de API

#### Formularios y Mensajes
- Labels de campos
- Mensajes de éxito/error
- Validaciones
- Confirmaciones

### 3. **Archivos de Traducción**
```
locale/
├── en/
│   └── LC_MESSAGES/
│       ├── django.po    (archivo fuente de traducciones)
│       └── django.mo    (archivo compilado binario)
└── es/
    └── LC_MESSAGES/
        ├── django.po
        └── django.mo
```

### 4. **Configuración Django**

#### settings.py
```python
# Idioma por defecto
LANGUAGE_CODE = 'es'

# Activar internacionalización
USE_I18N = True

# Idiomas disponibles
LANGUAGES = [
    ('es', _('Spanish')),
    ('en', _('English')),
]

# Ruta de archivos de traducción
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
```

#### urls.py
```python
from django.conf.urls.i18n import i18n_patterns

# Ruta para cambio de idioma
urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
]

# Rutas con soporte multiidioma
urlpatterns += i18n_patterns(
    path("", include("catalog.urls")),
    path("admin/", admin.site.urls),
    prefix_default_language=False,
)
```

#### Middleware
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # ← Importante
    'django.middleware.common.CommonMiddleware',
    # ...
]
```

---

## 📖 Uso del Sistema

### Para Usuarios

1. **Cambiar Idioma**:
   - Click en el selector de idioma en la navbar (🇪🇸 ES / 🇬🇧 EN)
   - El cambio es inmediato
   - Se mantiene la página actual
   - El idioma se guarda en la sesión

2. **Idioma por Defecto**:
   - El sitio detecta automáticamente el idioma del navegador
   - Si no está disponible, usa Español como predeterminado

3. **Persistencia**:
   - El idioma seleccionado se mantiene durante toda la sesión
   - Se guarda en una cookie llamada `django_language`

### Para Desarrolladores

#### 1. Agregar Nuevas Traducciones

**En Templates (.html):**
```django
{% load i18n %}

{# Texto simple #}
{% trans "Texto a traducir" %}

{# Variables #}
{% blocktrans %}Hola {{ username }}{% endblocktrans %}

{# Asignar a variable #}
{% translate "Ordenar por" as ph_order %}
```

**En Python (views.py, forms.py):**
```python
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

# En funciones
mensaje = _("Este es un mensaje")

# En definiciones de clase (usar lazy)
class MiForm(forms.Form):
    nombre = forms.CharField(label=_lazy("Nombre"))
```

#### 2. Actualizar Archivos de Traducción

**Opción A: Manual**

Edita directamente los archivos `.po`:
```
locale/en/LC_MESSAGES/django.po
locale/es/LC_MESSAGES/django.po
```

Formato:
```po
msgid "Texto en español"
msgstr "Text in English"
```

**Opción B: Con gettext (si está instalado)**

```powershell
# Extraer nuevas cadenas traducibles
python manage.py makemessages -l en
python manage.py makemessages -l es

# Editar los archivos .po generados

# Compilar
python manage.py compilemessages
```

**Opción C: Script personalizado (sin gettext)**

```powershell
# Compilar con nuestro script
python compile_translations.py
```

#### 3. Agregar Nuevo Idioma

1. Agregar en `settings.py`:
```python
LANGUAGES = [
    ('es', _('Spanish')),
    ('en', _('English')),
    ('fr', _('French')),  # Nuevo idioma
]
```

2. Crear estructura:
```
mkdir -p locale/fr/LC_MESSAGES
```

3. Crear archivo `locale/fr/LC_MESSAGES/django.po`:
```po
msgid ""
msgstr ""
"Language: fr\n"
"Content-Type: text/plain; charset=UTF-8\n"

msgid "Productos"
msgstr "Produits"
# ... más traducciones
```

4. Compilar:
```powershell
python compile_translations.py
```

5. Actualizar selector en `base.html`:
```html
<option value="fr" {% if LANGUAGE_CODE == 'fr' %}selected{% endif %}>🇫🇷 FR</option>
```

---

## 🎨 Personalización del Selector

El selector de idioma tiene estilos personalizados en `static/css/site.css`:

```css
.form-select.bg-transparent {
  background-color: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(255, 255, 255, 0.3) !important;
  color: white !important;
  /* ... más estilos */
}
```

Para cambiar banderas o formato:
```html
<!-- En base.html -->
<option value="es">🇪🇸 Español</option>
<option value="en">🇬🇧 English</option>
```

---

## 🔍 Verificación y Testing

### Probar el Sistema

1. **Acceder al sitio**:
   ```
   http://192.168.1.11:8000/
   ```

2. **Cambiar idioma**:
   - Click en selector ES/EN
   - Verificar que todo el contenido cambia
   - Navegar entre páginas (debe mantener el idioma)

3. **Verificar páginas**:
   - ✅ Home (`/`)
   - ✅ Lista de productos (`/products/`)
   - ✅ Páginas aliadas (`/partner-products/`)
   - ✅ Categorías (`/categorias/`)
   - ✅ Tiendas (`/tiendas/`)
   - ✅ Detalle de producto (`/products/<id>/`)

### Verificar Archivos Compilados

```powershell
# Verificar que existen los archivos .mo
ls locale/*/LC_MESSAGES/*.mo
```

Deberías ver:
```
locale/en/LC_MESSAGES/django.mo
locale/es/LC_MESSAGES/django.mo
```

---

## 📊 Estadísticas de Traducción

| Categoría | Cadenas Traducidas |
|-----------|-------------------|
| Navegación | 15 |
| Productos | 35 |
| Filtros y Ordenamiento | 20 |
| Formularios | 15 |
| Mensajes | 12 |
| Autenticación | 8 |
| API Externa | 5 |
| Otros | 10 |
| **TOTAL** | **120+** |

---

## 🐛 Troubleshooting

### El idioma no cambia

1. Verificar que el middleware está configurado:
```python
# settings.py
'django.middleware.locale.LocaleMiddleware',
```

2. Verificar archivos .mo compilados:
```powershell
python compile_translations.py
```

3. Reiniciar servidor:
```powershell
python manage.py runserver 0.0.0.0:8000
```

### Algunas cadenas no se traducen

1. Verificar que el template carga i18n:
```django
{% load i18n %}
```

2. Verificar que usa la etiqueta trans:
```django
{% trans "Texto" %}
```

3. Agregar traducción en archivos .po y recompilar

### Error "Can't find msgfmt"

Usar nuestro script personalizado:
```powershell
python compile_translations.py
```

---

## 📝 Mejores Prácticas

### 1. Siempre usar `{% load i18n %}` al inicio del template

### 2. Para textos dinámicos, usar blocktrans:
```django
{% blocktrans count counter=list|length %}
  Hay {{ counter }} producto
{% plural %}
  Hay {{ counter }} productos
{% endblocktrans %}
```

### 3. En Python, usar lazy para definiciones de clase:
```python
from django.utils.translation import gettext_lazy as _

class Meta:
    verbose_name = _("Producto")
```

### 4. Compilar después de editar .po:
```powershell
python compile_translations.py
```

### 5. Mantener consistencia en las traducciones:
- Usar mismo estilo en todo el sitio
- Revisar contexto antes de traducir
- Mantener longitud similar para UI

---

## 🚀 Siguiente Nivel

### Detección Automática de Idioma
```python
# En middleware o view
from django.utils import translation

def activate_user_language(request):
    lang = request.META.get('HTTP_ACCEPT_LANGUAGE', 'es')[:2]
    if lang in ['es', 'en']:
        translation.activate(lang)
```

### URLs con Prefijo de Idioma
```python
# urls.py
urlpatterns += i18n_patterns(
    path("", include("catalog.urls")),
    prefix_default_language=True,  # /es/products/, /en/products/
)
```

### Traducción de Contenido de Base de Datos
Usar paquetes como `django-modeltranslation` o `django-parler`

---

## ✅ Estado Actual

- ✅ Configuración completa
- ✅ Archivos de traducción creados (EN/ES)
- ✅ Archivos compilados (.mo)
- ✅ Selector de idioma funcional
- ✅ Todas las páginas traducidas
- ✅ Estilos personalizados
- ✅ Persistencia de idioma
- ✅ Documentación completa

---

## 📞 Soporte

Para agregar nuevas traducciones o idiomas:
1. Editar archivos en `locale/<lang>/LC_MESSAGES/django.po`
2. Ejecutar `python compile_translations.py`
3. Reiniciar servidor

---

**Última actualización**: 23 de Noviembre, 2025  
**Versión**: 1.0  
**Idiomas soportados**: Español (ES), English (EN)

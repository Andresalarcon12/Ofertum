# Ofertum

Agregador de descuentos y ofertas que permite a los usuarios buscar productos, filtrar por categorías, tiendas y precios, además de ver productos de páginas aliadas.

## 🌟 Características Principales

- 🔍 Búsqueda y filtrado avanzado de productos
- 🏷️ Gestión de categorías y tiendas
- 💰 Filtros por rango de precios
- ⭐ Sistema de reseñas y valoraciones
- 📊 Reportes exportables (PDF y Excel)
- 🌐 **Integración con APIs externas de socios aliados**
- 🔐 Sistema de autenticación y propuestas de productos
- 🌍 **Soporte multiidioma completo (Español/Inglés)** 🆕
- 📱 Diseño responsive y accesible desde dispositivos móviles

## 🚀 Instalación y Configuración

### 1. Instala dependencias:

```powershell
pip install -r requirements.txt
```

### 2. Aplica migraciones:

```powershell
python manage.py migrate
```

### 3. Crea un superusuario para acceder al admin y moderar propuestas:

```powershell
python manage.py createsuperuser
```

### 4. Ejecuta el servidor de desarrollo:

```powershell
python manage.py runserver
```

## 📍 Rutas Principales

### Frontend
- **Home**: http://127.0.0.1:8000/
- **Productos**: http://127.0.0.1:8000/products/
- **Categorías**: http://127.0.0.1:8000/categorias/
- **Tiendas**: http://127.0.0.1:8000/tiendas/
- **Páginas Aliadas**: http://127.0.0.1:8000/partner-products/ 🆕
- **Enviar propuesta**: http://127.0.0.1:8000/proposals/submit/
- **Añadir/editar reseña**: http://127.0.0.1:8000/products/<id>/review/

### Admin
- **Panel de moderación**: http://127.0.0.1:8000/proposals/admin/ (requiere staff)
- **Django Admin**: http://127.0.0.1:8000/admin/

### API JSON Propia
- **Lista de productos**: http://127.0.0.1:8000/api/products/
- **Detalle de producto**: http://127.0.0.1:8000/api/products/<id>/
- **Exportar reporte (PDF)**: http://127.0.0.1:8000/products/export/?format=pdf
- **Exportar reporte (Excel)**: http://127.0.0.1:8000/products/export/?format=xlsx

## 🔗 Integración con APIs Externas

Este proyecto incluye integración con APIs externas de socios aliados:

- **API de Socios**: http://13.218.169.6/api/productos/
- **Vista dedicada**: Accesible desde "Páginas Aliadas" en el menú de navegación
- **Características**: Filtros, ordenamiento, paginación, manejo de errores

### Documentación Completa
Para información detallada sobre la integración de APIs externas y recomendaciones de APIs públicas, consulta:

📖 **[INTEGRACION_API_EXTERNA.md](./INTEGRACION_API_EXTERNA.md)**

Este documento incluye:
- Detalles de la API de socios implementada
- Recomendaciones de APIs públicas (Fake Store API, DummyJSON, Best Buy, eBay, etc.)
- Ejemplos de código para integración
- Comparativa de APIs
- Buenas prácticas

## 🌍 Sistema Multiidioma

El proyecto cuenta con soporte completo para **Español (ES)** e **Inglés (EN)**:

- **Selector visual** en la barra de navegación con banderas 🇪🇸 🇬🇧
- **120+ cadenas traducidas** cubriendo toda la interfaz
- **Persistencia de idioma** durante la sesión
- **Detección automática** del idioma del navegador
- **Traducciones compiladas** para máximo rendimiento

### Características Traducidas:
- ✅ Navegación completa
- ✅ Filtros y búsquedas
- ✅ Productos y detalles
- ✅ Formularios y mensajes
- ✅ Páginas aliadas
- ✅ Sistema de autenticación

### Documentación Completa
Para agregar nuevos idiomas o modificar traducciones, consulta:

📖 **[SISTEMA_MULTIIDIOMA.md](./SISTEMA_MULTIIDIOMA.md)**

Este documento incluye:
- Guía de uso del sistema
- Cómo agregar nuevas traducciones
- Cómo agregar nuevos idiomas
- Troubleshooting
- Mejores prácticas

## 🛠️ Tecnologías Utilizadas

- **Framework**: Django 5.2.5
- **Frontend**: Bootstrap 5.3.3, Bootstrap Icons
- **Base de datos**: SQLite (desarrollo)
- **Reportes**: ReportLab (PDF), CSV para Excel
- **APIs**: requests para integraciones externas
- **Internacionalización**: Django i18n

## 📦 Dependencias Principales

- Django 5.2.5
- Pillow (manejo de imágenes)
- reportlab (generación de PDFs)
- pandas, openpyxl (procesamiento de datos)
- requests (consumo de APIs externas) 🆕
- polib (traducciones)

## 🎨 Características de Diseño

- Diseño responsive con Bootstrap
- Animaciones y efectos visuales modernos
- Fondo con gradientes dinámicos (canvas orbs)
- Cards con efectos de elevación
- Sistema de badges y pills para categorías
- Tema de colores consistente (púrpura/cyan)

## 🌍 Multiidioma

El proyecto soporta Español (es) e Inglés (en):
- **Selector visual** con banderas en la barra de navegación
- **120+ cadenas traducidas**
- Traducciones en plantillas con `{% trans %}`
- Archivos de traducción compilados en `locale/`
- **Cambio instantáneo** sin recargar página
- **Persistencia** de idioma durante la sesión

Para más detalles: [SISTEMA_MULTIIDIOMA.md](./SISTEMA_MULTIIDIOMA.md)

## 👥 Usuarios y Permisos

### Usuario Regular
- Ver productos y detalles
- Buscar y filtrar
- Enviar propuestas de productos
- Dejar reseñas y valoraciones

### Usuario Staff (Admin)
- Todas las capacidades de usuario regular
- Moderar propuestas (aprobar/rechazar)
- Acceso al panel de administración Django

## 📊 Sistema de Reportes

Exporta productos filtrados en dos formatos:
- **PDF**: Reporte formateado con ReportLab
- **Excel (CSV)**: Compatible con Excel, LibreOffice

Los reportes respetan todos los filtros aplicados (búsqueda, categoría, tienda, precio, rating).

## 🔐 Seguridad

- Autenticación de Django
- Decoradores `@login_required` para acciones protegidas
- Decoradores `@user_passes_test` para acceso de staff
- CSRF protection habilitado
- Validación de formularios

## 🚦 Próximas Mejoras Sugeridas

- [ ] Sistema de cache para APIs externas
- [ ] Implementar Fake Store API como segunda fuente
- [ ] Tests automatizados
- [ ] API REST con Django REST Framework
- [ ] Sistema de favoritos
- [ ] Notificaciones de nuevas ofertas
- [ ] Comparador de precios entre tiendas
- [ ] Más idiomas (Francés, Portugués, etc.)

## 📝 Notas de Desarrollo

- La paginación muestra 9 productos por página
- Las ofertas se calculan dinámicamente desde el modelo `Oferta`
- Los ratings se calculan con agregación de Django (`Avg`, `Count`)
- Las imágenes de productos externos se convierten a URLs absolutas

## 📞 Soporte

Para dudas sobre implementación o bugs:
1. Revisar la documentación:
   - [INTEGRACION_API_EXTERNA.md](./INTEGRACION_API_EXTERNA.md) - APIs externas
   - [SISTEMA_MULTIIDIOMA.md](./SISTEMA_MULTIIDIOMA.md) - Traducciones
2. Consultar el código fuente comentado
3. Verificar logs de Django para debugging

## 📱 Acceso desde Dispositivos Móviles

Para acceder desde tu celular en la misma red Wi-Fi:

1. Asegúrate de que tu celular esté conectado a la misma red que tu computadora
2. Inicia el servidor con:
   ```powershell
   python manage.py runserver 0.0.0.0:8000
   ```
3. Accede desde tu celular a: `http://192.168.1.11:8000/`
   *(Reemplaza la IP con la de tu computadora)*

---

**Última actualización**: Noviembre 23, 2025
**Versión**: 2.1 - Sistema Multiidioma Completo

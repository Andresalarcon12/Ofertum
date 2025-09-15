# Ofertum

## Nuevas funcionalidades añadidas

- Propuestas moderadas: los usuarios autenticados pueden enviar propuestas de productos desde `/proposals/submit/`.
- Moderación: los administradores (staff) pueden ver propuestas en `/proposals/admin/` y aprobar/rechazarlas. Al aprobarse se crea un `Producto` visible públicamente.
- Comentarios y valoraciones: usuarios autenticados pueden comentar y puntuar (1-5) productos en la ficha del producto; una reseña por usuario/por producto, editable por su autor.

## Migraciones y uso

1. Instala dependencias (usa tu entorno virtual):

```powershell
pip install -r requirements.txt
```

2. Aplica migraciones:

```powershell
python manage.py migrate
```

3. Crea un superusuario para acceder al admin y moderar propuestas:

```powershell
python manage.py createsuperuser
```

4. Ejecuta el servidor de desarrollo:

```powershell
python manage.py runserver
```

5. Rutas principales:

- Enviar propuesta: /proposals/submit/
- Moderación (admin): /proposals/admin/ (requiere staff)
- Añadir/editar reseña: /products/<id>/review/

Notas: las plantillas y la lógica son intencionadamente simples y pensadas para un entorno de desarrollo.
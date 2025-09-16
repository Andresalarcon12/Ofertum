# Ofertum
## Migraciones y uso

1. Instala dependencias:

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

- Enviar propuesta: http://127.0.0.1:8000/proposals/submit/
- Moderación (admin): http://127.0.0.1:8000/admin/ (requiere staff)
- Añadir/editar reseña: http://127.0.0.1:8000/products/<id>/review/

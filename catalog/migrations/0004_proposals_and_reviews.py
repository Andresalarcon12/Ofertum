# Generated migration for Proposal and Review models (minimal)
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_alter_oferta_options_remove_oferta_fecha_fin_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre')),
                ('descripcion', models.TextField(blank=True, verbose_name='Descripción')),
                ('categoria', models.CharField(blank=True, db_index=True, max_length=100, verbose_name='Categoría')),
                ('tienda', models.CharField(blank=True, db_index=True, max_length=150, verbose_name='Tienda')),
                ('link', models.URLField(blank=True, verbose_name='Enlace del producto')),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='proposals/', verbose_name='Imagen')),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio')),
                ('creado', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de propuesta')),
                ('status', models.CharField(default='pending', max_length=20, choices=[('pending', 'Pendiente'), ('approved', 'Aprobada'), ('rejected', 'Rechazada')], verbose_name='Estado')),
                ('admin_note', models.TextField(blank=True, verbose_name='Nota del moderador')),
                ('approved_at', models.DateTimeField(blank=True, null=True, verbose_name='Aprobada en')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proposals', to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Propuesta',
                'verbose_name_plural': 'Propuestas',
                'ordering': ['-creado'],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(verbose_name='Puntuación')),
                ('comentario', models.TextField(blank=True, verbose_name='Comentario')),
                ('creado', models.DateTimeField(auto_now_add=True, verbose_name='Creado')),
                ('actualizado', models.DateTimeField(auto_now=True, verbose_name='Actualizado')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='catalog.producto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Reseña',
                'verbose_name_plural': 'Reseñas',
                'ordering': ['-creado'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='review',
            unique_together={('producto', 'usuario')},
        ),
    ]

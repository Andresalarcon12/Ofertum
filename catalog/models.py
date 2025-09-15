from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse


class Producto(models.Model):
    """Modelo que representa un producto del catálogo."""
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    # Índices para filtrar por categoría y tienda de forma eficiente
    categoria = models.CharField('Categoría', max_length=100, blank=True, db_index=True)
    tienda = models.CharField('Tienda', max_length=150, blank=True, db_index=True)

    link = models.URLField('Enlace del producto', blank=True)
    imagen = models.ImageField('Imagen', upload_to='productos/', null=True, blank=True)
    precio = models.DecimalField(
        'Precio', max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    creado = models.DateTimeField('Fecha de creación', auto_now_add=True)
    disponible = models.BooleanField('Disponible', default=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    # ---- Helpers útiles para routing/plantillas ----
    @property
    def categoria_slug(self) -> str:
        return slugify(self.categoria) if self.categoria else ''

    @property
    def tienda_slug(self) -> str:
        return slugify(self.tienda) if self.tienda else ''

    def get_absolute_url(self):
        # Útil para enlazar al detalle sin hardcodear la ruta
        return reverse('catalog:product_detail', args=[self.pk])

    # ---- Lógica de precios/ofertas existente ----
    def obtener_oferta_activa(self):
        """Devuelve la oferta activa más reciente para este producto, o None.

        Ya que las ofertas no usan fechas, se toma la oferta marcada `activo=True`
        más reciente (por id) si existe.
        """
        ofertas = self.ofertas.filter(activo=True)
        return ofertas.order_by('-id').first()

    def obtener_precio_actual(self):
        """Retorna el precio vigente del producto considerando la oferta activa si existe."""
        oferta = self.obtener_oferta_activa()
        if not oferta:
            return self.precio

        # Si la oferta define un precio fijo, lo usamos.
        if oferta.precio_fijo is not None:
            return oferta.precio_fijo

        # Aplicar porcentaje de descuento sobre el precio base.
        descuento = (oferta.descuento_porcentaje or Decimal('0')) / Decimal('100')
        precio_descuento = (self.precio * (Decimal('1') - descuento)).quantize(Decimal('0.01'))
        return precio_descuento


class Oferta(models.Model):
    """Modelo que representa una oferta aplicada a un producto.

    Se puede definir un `precio_fijo` (opcional) o un `descuento_porcentaje`.
    La vigencia se controla con el campo `activo`.
    """
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='ofertas',
        verbose_name='Producto',
    )
    descuento_porcentaje = models.DecimalField(
        'Descuento (%)', max_digits=5, decimal_places=2, default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
    )
    precio_fijo = models.DecimalField(
        'Precio de oferta', max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Si se establece, este precio reemplaza al precio con descuento',
    )
    activo = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Oferta'
        verbose_name_plural = 'Ofertas'
        # ordenar por id (las ofertas más recientes primero)
        ordering = ['-id']

    def __str__(self):
        etiqueta = f"{self.descuento_porcentaje}%" if self.precio_fijo is None else f"Precio {self.precio_fijo}"
        return f'Oferta ({etiqueta}) - {self.producto.nombre}'

    def esta_activa(self):
        """Indica si la oferta está marcada como activa."""
        return bool(self.activo)

    def precio_oferta(self):
        """Calcula el precio de la oferta (ya sea precio_fijo o aplicado sobre el precio del producto)."""
        if self.precio_fijo is not None:
            return self.precio_fijo
        descuento = (self.descuento_porcentaje or Decimal('0')) / Decimal('100')
        precio = (self.producto.precio * (Decimal('1') - descuento)).quantize(Decimal('0.01'))
        return precio


from django.conf import settings


class Proposal(models.Model):
    """Propuesta de producto enviada por un usuario (pendiente de moderación).

    No se debe permitir que usuarios normales creen `Producto` directamente;
    en su lugar envían propuestas que los administradores pueden aprobar o rechazar.
    """
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendiente'),
        (STATUS_APPROVED, 'Aprobada'),
        (STATUS_REJECTED, 'Rechazada'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='proposals',
        verbose_name='Usuario',
    )
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    categoria = models.CharField('Categoría', max_length=100, blank=True, db_index=True)
    tienda = models.CharField('Tienda', max_length=150, blank=True, db_index=True)
    link = models.URLField('Enlace del producto', blank=True)
    imagen = models.ImageField('Imagen', upload_to='proposals/', null=True, blank=True)
    precio = models.DecimalField(
        'Precio', max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    creado = models.DateTimeField('Fecha de propuesta', auto_now_add=True)
    status = models.CharField('Estado', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    admin_note = models.TextField('Nota del moderador', blank=True)
    approved_at = models.DateTimeField('Aprobada en', null=True, blank=True)

    class Meta:
        verbose_name = 'Propuesta'
        verbose_name_plural = 'Propuestas'
        ordering = ['-creado']

    def __str__(self):
        return f"{self.nombre} ({self.usuario}) - {self.get_status_display()}"


class Review(models.Model):
    """Comentarios y calificaciones de productos por usuarios autenticados.

    - rating: 1..5
    - Cada usuario puede tener una única review por producto (unique_together)
    """
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='reviews')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField('Puntuación', validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField('Comentario', blank=True)
    creado = models.DateTimeField('Creado', auto_now_add=True)
    actualizado = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
        unique_together = (('producto', 'usuario'),)
        ordering = ['-creado']

    def __str__(self):
        return f"{self.producto.nombre} - {self.usuario} ({self.rating})"


    
    # ---------- Helper properties on Producto (attached dynamically) ----------


def producto_avg_rating(self):
    qs = self.reviews.all()
    if not qs.exists():
        return None
    return qs.aggregate(avg=models.Avg('rating'))['avg']


def producto_rating_count(self):
    return self.reviews.count()


# attach helper properties to Producto for templates convenience
Producto.avg_rating = property(producto_avg_rating)
Producto.rating_count = property(producto_rating_count)

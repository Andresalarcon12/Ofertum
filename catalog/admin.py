from django.contrib import admin

from .models import Producto, Oferta


class OfertaInline(admin.TabularInline):
	model = Oferta
	extra = 1
	fields = ('descuento_porcentaje', 'precio_fijo', 'activo')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'precio', 'disponible', 'creado')
	search_fields = ('nombre', 'descripcion')
	list_filter = ('disponible',)
	inlines = [OfertaInline]


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
	list_display = ('producto', 'descuento_porcentaje', 'precio_fijo', 'activo')
	search_fields = ('producto__nombre',)
	list_filter = ('activo',)


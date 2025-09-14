from django.contrib import admin
from .models import Producto, Oferta


class OfertaInline(admin.TabularInline):
    model = Oferta
    extra = 1
    fields = ("descuento_porcentaje", "precio_fijo", "activo")
    show_change_link = True


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "id", "nombre", "categoria", "tienda",
        "precio", "precio_actual", "disponible", "creado",
    )
    search_fields = ("nombre", "descripcion", "categoria", "tienda")
    list_filter = ("disponible", "categoria", "tienda")
    ordering = ("nombre",)
    inlines = [OfertaInline]

    @admin.display(description="Precio vigente")
    def precio_actual(self, obj: Producto):
        return obj.obtener_precio_actual()


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = (
        "id", "producto", "tienda_producto",
        "descuento_porcentaje", "precio_fijo", "precio_oferta_calc", "activo",
    )
    search_fields = ("producto__nombre",)
    list_filter = ("activo",)

    @admin.display(description="Tienda")
    def tienda_producto(self, obj: Oferta):
        # la tienda está en Producto
        return obj.producto.tienda

    @admin.display(description="Precio oferta")
    def precio_oferta_calc(self, obj: Oferta):
        return obj.precio_oferta()



admin.site.site_header = "Ofertum – Administración"
admin.site.site_title = "Ofertum Admin"
admin.site.index_title = "Panel principal"


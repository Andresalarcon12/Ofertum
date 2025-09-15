from django.contrib import admin
from .models import Producto, Oferta
from .models import Proposal, Review


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


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "usuario", "categoria", "tienda", "precio", "status", "creado")
    list_filter = ("status", "categoria", "tienda")
    search_fields = ("nombre", "descripcion", "usuario__username")
    actions = ("approve_selected", "reject_selected")

    def approve_selected(self, request, queryset):
        from django.utils import timezone
        approved = 0
        for obj in queryset.filter(status=Proposal.STATUS_PENDING):
            # Create Producto from proposal
            Producto.objects.create(
                nombre=obj.nombre,
                descripcion=obj.descripcion,
                categoria=obj.categoria,
                tienda=obj.tienda,
                link=obj.link,
                imagen=obj.imagen,
                precio=obj.precio,
                disponible=True,
            )
            obj.status = Proposal.STATUS_APPROVED
            obj.approved_at = timezone.now()
            obj.save()
            approved += 1
        self.message_user(request, f"{approved} propuestas aprobadas y convertidas en productos.")
    approve_selected.short_description = "Aprobar y convertir en producto"

    def reject_selected(self, request, queryset):
        rejected = queryset.filter(status=Proposal.STATUS_PENDING).update(status=Proposal.STATUS_REJECTED)
        self.message_user(request, f"{rejected} propuestas rechazadas.")
    reject_selected.short_description = "Rechazar propuestas"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "producto", "usuario", "rating", "creado")
    search_fields = ("producto__nombre", "usuario__username", "comentario")
    list_filter = ("rating",)


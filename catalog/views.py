from decimal import Decimal, InvalidOperation

from django.db.models import Q, Count
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify

from .models import Producto


def home(request):
    return render(request, "catalog/home.html")


def product_list(request):
    """
    Lista de productos con filtros por:
    - q: texto (nombre/descripcion)
    - category: categoría exacta (case-insensitive)
    - store: tienda exacta (case-insensitive)
    - min / max: precio vigente (considerando oferta activa) en rango
    """
    q = (request.GET.get("q") or "").strip()
    category = (request.GET.get("category") or "").strip()
    store = (request.GET.get("store") or "").strip()
    price_min = (request.GET.get("min") or "").strip()
    price_max = (request.GET.get("max") or "").strip()

    # Base queryset
    qs = Producto.objects.filter(disponible=True)

    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))

    if category:
        qs = qs.filter(categoria__iexact=category)

    if store:
        qs = qs.filter(tienda__iexact=store)

    productos = qs.order_by("nombre")

    # Parseo de límites de precio (trabajamos con Decimal)
    min_dec = max_dec = None
    try:
        if price_min:
            min_dec = Decimal(price_min.replace(",", "."))
        if price_max:
            max_dec = Decimal(price_max.replace(",", "."))
    except InvalidOperation:
        # Si el usuario mete texto no numérico, ignoramos los límites
        min_dec = max_dec = None

    # Construcción de items y filtro por precio vigente en Python
    items = []
    for p in productos:
        vigente = p.obtener_precio_actual()  # Decimal
        if min_dec is not None and vigente < min_dec:
            continue
        if max_dec is not None and vigente > max_dec:
            continue

        items.append({
            "name": p.nombre,
            "price": vigente,
            "store": p.tienda,
            "category": p.categoria,
            "producto_obj": p,   # por si tu template lo usa
        })

    ctx = {
        "q": q, "category": category, "store": store,
        "price_min": price_min, "price_max": price_max,
        "items": items,
    }
    return render(request, "catalog/product_list.html", ctx)


#  CATEGORÍAS 
def categories(request):
    """
    Lista de categorías existentes (derivadas de Producto.categoria),
    con total de productos por categoría.
    """
    cats_qs = (
        Producto.objects.filter(disponible=True)
        .exclude(categoria__isnull=True)
        .exclude(categoria__exact="")
        .values("categoria")
        .annotate(total=Count("id"))
        .order_by("categoria")
    )
    cats = [
        {
            "name": c["categoria"],
            "slug": slugify(c["categoria"]),
            "count": c["total"],
        }
        for c in cats_qs
    ]
    return render(request, "catalog/categories.html", {"cats": cats})


def category_detail(request, slug):
    """
    Muestra productos de una categoría, resolviendo el nombre por slug.
    """
    all_cats = list(
        Producto.objects.exclude(categoria__isnull=True)
        .exclude(categoria__exact="")
        .values_list("categoria", flat=True)
        .distinct()
    )
    cat_name = next((c for c in all_cats if slugify(c) == slug), None)
    if not cat_name:
        raise Http404("Categoría no encontrada")

    qs = (
        Producto.objects.filter(disponible=True, categoria__iexact=cat_name)
        .order_by("nombre")
    )

    items = [{
        "name": p.nombre,
        "price": p.obtener_precio_actual(),
        "store": p.tienda,
        "category": p.categoria,
        "producto_obj": p,
    } for p in qs]

    ctx = {
        "items": items,
        "q": "", "category": cat_name, "store": "",
        "price_min": "", "price_max": "",
    }
    return render(request, "catalog/product_list.html", ctx)


# TIENDAS 
def stores(request):
    """
    Lista de tiendas existentes (derivadas de Producto.tienda),
    con total de productos por tienda.
    """
    stores_qs = (
        Producto.objects.filter(disponible=True)
        .exclude(tienda__isnull=True)
        .exclude(tienda__exact="")
        .values("tienda")
        .annotate(total=Count("id"))
        .order_by("tienda")
    )
    stores = [
        {
            "name": s["tienda"],
            "slug": slugify(s["tienda"]),
            "count": s["total"],
        }
        for s in stores_qs
    ]
    return render(request, "catalog/stores.html", {"stores": stores})


def store_detail(request, slug):
    """
    Muestra productos de una tienda, resolviendo el nombre por slug.
    """
    all_stores = list(
        Producto.objects.exclude(tienda__isnull=True)
        .exclude(tienda__exact="")
        .values_list("tienda", flat=True)
        .distinct()
    )
    store_name = next((s for s in all_stores if slugify(s) == slug), None)
    if not store_name:
        raise Http404("Tienda no encontrada")

    qs = (
        Producto.objects.filter(disponible=True, tienda__iexact=store_name)
        .order_by("nombre")
    )

    items = [{
        "name": p.nombre,
        "price": p.obtener_precio_actual(),
        "store": p.tienda,
        "category": p.categoria,
        "producto_obj": p,
    } for p in qs]

    ctx = {
        "items": items,
        "q": "", "category": "", "store": store_name,
        "price_min": "", "price_max": "",
    }
    return render(request, "catalog/product_list.html", ctx)



def detalle_producto(request, pk):
    """Vista de detalle para un producto."""
    producto = get_object_or_404(Producto, pk=pk)
    oferta = producto.obtener_oferta_activa()
    return render(request, "catalog/product_detail.html", {
        "producto": producto,
        "oferta": oferta,
    })
